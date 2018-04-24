
import redis
import configparser
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# read config file
config = configparser.ConfigParser()
cfgpath = os.path.join(BASE_DIR, "config/db.conf")
print(cfgpath)
config.read(cfgpath)


class Queue(object):
    def __init__(self):
        self.r= redis.Redis(host=config.get('redis','host'), port=config.get('redis','port'),password=config.get('redis','password'))
        self.queue_name='crawl_weibo'

    def push(self,start_data,queue_name='crawl_weibo'):
        self.queue_name=queue_name  #当前队列名
        self.r.lpush(queue_name,start_data) #入队
        self.r.expire(queue_name,3600)  #设置1小时的过期时间
        return True

    def pop(self):
        data=str(self.r.brpop(self.queue_name)[1],encoding='utf-8')  #阻塞型等待出队数据
        return data