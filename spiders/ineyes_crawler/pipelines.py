
import redis
import re
from scrapy.exceptions import DropItem
import time
from datetime import datetime
import json
#---------redis config---------
redis_host="139.198.4.56"
redis_port=6379
redis_password='LtmJ16w9lZ'
timeout=100



dont_fliter=['response','author_home']
count=0
class IneyesCrawlerPipeline(object):
    """
    清洗数据的html标签
    """
    def process_item(self, item, spider):
        re_h = re.compile('</?\w+[^>]*>')
        for k,v in item.items():     #清除html标签
            if k in dont_fliter:  #不清洗测试响应
                item[k] = v
                continue
            datas=[]
            for i in v:  #对提取列表进行逐一清洗
                data= re_h.sub('', i).strip()  #去掉html标签和两头的空格
                datas.append(data)
            item[k]=datas
        for field in spider.config['fields']:  #对空值进行处理，不丢弃空值
            if not item.get(field):
                item[field] = ""
        spider.log("数据清洗完毕")
        return item

class PubSubPipeline(object):
    """
    处理item，并发布到指定的redis频道中
    """

    def __init__(self):
        self.r = redis.Redis(host=redis_host, port=redis_port,socket_timeout=timeout,password=redis_password)
    def process_item(self,item, spider):  #采取redis消息队列的发布者模式
        if "test_ineyes" in spider.name :
            #todo 使用logging模块内方法 直接提取日志数据
            item.set(["log","rules"])   #添加log,rules属性s
            item['rules'] = spider.config['fields']
            item['timestamp']=time.time()
            item['source'] = spider.source
            spider.log(" 测试数据: %s 发布成功! "%item['url'])
            spider.end_time=datetime.now()
            spider.log("总共耗时: %s 秒"%str((spider.end_time-spider.start_time).seconds))
            item["log"] = str(spider.test_logs)
            self.r.publish(spider.channel,json.dumps(dict(item)))
            raise DropItem("丢弃已成功发布的测试数据结果")
        else:
            item['id']=spider.seed_id
            item['source'] = spider.source
            item['timestamp']=time.time()     #这三个值是共有的三个唯一值，其他值都为list，允许提取多元素
            self.r.publish(spider.channel,json.dumps(dict(item)))   #将正常种子发布的数据，发布到指定频道
            spider.log(" 正常抓取数据 %s 发布成功！"%item['url'])
            return item
