from scrapy_redis.scheduler import Scheduler
from scrapy.utils.misc import load_object



class Seed_Scheduler(Scheduler):

    def update_queue(self):
        """更新请求队列的key，保证实时与种子唯一相关"""
        #todo 当前更新队列key采用有入队即更新的方式，有效但效率低，待有更好的方案再解决
        try:
            self.queue = load_object(self.queue_cls)(
                server=self.server,
                spider=self.spider,
                key=self.queue_key % {'spider': self.spider.name},
                serializer=self.serializer,
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

    def enqueue_request(self, request):
        self.update_queue()
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return False
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.queue.push(request)
        return True




