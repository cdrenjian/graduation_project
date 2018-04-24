import redis
from ineyes_crawler.seeds_mysql import SeedsMysql
import logging
import time
from ineyes_crawler.config import redis_config
logger=logging.getLogger()


class SeedsQueue(object):
    """
    该类用于对种子队列进行操作
    """

    def __init__(self):
        self.r = redis.Redis(host=redis_config['redis_host'], port=redis_config['redis_port'],socket_timeout=redis_config['timeout'],password=redis_config['redis_password'])

    def push(self,queue_name,seed):
        """
        传入种子列表写入redis的对应seeds队列中
        """

        start_url_key = str(seed[0]['id']) + ":start_urls"  # 待爬取种子需要将urls分离出来单独入库，用于分布式共享
        for url in seed[1]:
            # 初始化start_url到redis中
            self.r.lpush(start_url_key, url)
            self.r.expire(start_url_key,3600)  #设置过期时间为3600秒
        self.r.lpush(queue_name,seed) #将完整种子信息放入队列中
        self.r.expire(queue_name, 3600)
        return True
    def update(self,queue_name="wait_queue"):
        """
        从Mysql库里更新符合状态的种子并添加到种子队列中
        """

        sm = SeedsMysql()
        seeds = []
        type=1 if queue_name=="wait_queue" else 2
        logger.info("在Mysql里查找种子中...")
        while not seeds:
            time.sleep(3)
            seeds = sm.get_seeds(type)  # 得到所有状态为1的种子
            self.r.delete(queue_name)
            for seed in seeds :
                self.push(queue_name,seed)
        logger.info("获得库里新种子：%s"%seeds)
        sm.close()


    def pop(self,queue_name):
        '''
        从队列中取出一个种子，返回列表格式，结果为包含配置字典和urls列表的列表
        该函数是阻塞性，如果队列为空，将会一直阻塞链接，不返回结果。
        '''

        str_data = self.r.brpop(queue_name)#长时间阻塞
        if str_data is not None:
            str_data=str_data[1]
        else:
            return None
        str_data = str_data.decode('utf-8')
          #直接用eval简单粗暴，json转换单双引号和redis相遇太坑
        if queue_name!='crawl_weibo':
            str_data = eval(str_data)
        return str_data

    def get_all(self,queue_name):  #暂时作为通用的list_key查询,目前只是用于查询队列是否空
        """
        暂时作为通用的list_key查询队列数据,目前只是用于查询队列是否空
        """

        try:
            all = self.r.lrange(queue_name,0,-1)
            all = [i.decode('utf-8') for i in all]
            all.reverse()    #通过倒置将后进入队列的种子放到末尾。
        except:
            return None
        return all    #返回的是以种子字符串构成的列表  #todo 字符串应转化为对象再返回

    def delete(self,queue_name):
        """
        根据key删除redis中的值
        """

        logger.info("清除 %s 队列成功"%queue_name)
        self.r.delete(queue_name)

squeue = SeedsQueue()  #利用模块只加载一次的特性，实现单例模式


