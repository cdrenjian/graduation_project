
import sys
import json
import logging
import redis
import threading
import configparser
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)
# read config file
config = configparser.ConfigParser()
cfgpath = os.path.join(BASE_DIR, "config/db.conf")
print(cfgpath)
config.read(cfgpath)





class Listener(object):
    """
    监听器，用于监听Redis订阅的data
    """
    def __init__(self):
        # self.r = redis.Redis(host='139.198.4.56', port='6379')
        self.redis_client = redis.Redis(host=config.get('redis','host'), port=config.get('redis','port'),password=config.get('redis','password'))
        self.crawl_seeds = self.redis_client.pubsub()
        self.crawl_seeds.subscribe('weibo_gp')
        # self.listen_data = listen_data

    def listen(self):
        global listen_data
        logging.info("开始订阅...")
        for item in self.crawl_seeds.listen():
            if item['type'] != 'message':
                continue
            meta = str(item['data'],encoding='utf-8')
            logging.info('得到通知：%s' % meta)
            listen_data.add(meta)

    def handler(self):
        global listen_data
        while True:
            if listen_data:
                data=listen_data.pop()
            else:
                continue
            data=json.loads(data)
            logging.info('开始处理：%s'%data)
            f=Fliter()
            data=f.trans_space(data)
            data['publish_date']=f.time_fliter(data['publish_date'])

class Fliter(object):
    def time_fliter(self,data):
        data=data.strip()

        if "小时前" in data or '昨天' in data or "天前" in data or "分钟前" in data:
            delta = datetime.timedelta()
            if "小时前" in data:
                data = data.replace("小时前", "")
                delta = datetime.timedelta(hours=int(data))
            elif "昨天" in data:
                delta = datetime.timedelta(days=1)
            elif "天前" in data:
                data = data.replace("天前", "")
                delta = datetime.timedelta(days=int(data))
            elif "分钟前" in data:
                data = data.replace("分钟前", "")
                delta = datetime.timedelta(minutes=int(data))
            now = datetime.datetime.now()
            result = now - delta
            return result.strftime('%Y-%m-%d %H:%M:%S')
        try:
            data=datetime.datetime.strptime(data,'%m月%d日 %H:%M')
            data=data.replace(datetime.datetime.now().year)
        except:
            try:
                data = datetime.datetime.strptime(data, '%Y年%m月%d日 %H:%M')
            except:
                return None
        logging.info('格式化后的时间:%s'%data)
        return data
    def trans_space(self,data):
        for k,v in data.items():
            data[k]=v.replace('\u200b',' ')
        logging.info('清除特殊符号后：%s'%data)
        return data



if __name__=='__main__':
    listen_data=set()
    l=Listener()
    t=threading.Thread(target=l.listen)
    t.start()
    l.handler()









