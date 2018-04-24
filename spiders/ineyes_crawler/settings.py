import random


BOT_NAME = 'ineyes_crawler'

SPIDER_MODULES = ['ineyes_crawler.spiders']
NEWSPIDER_MODULE = 'ineyes_crawler.spiders'
ROBOTSTXT_OBEY = False
TELNETCONSOLE_ENABLED = False
DOWNLOADER_MIDDLEWARES = {
    # 'ineyes_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
    'ineyes_crawler.middlewares.SubUserAgentMiddleware': 100,
    'ineyes_crawler.middlewares.PhantomJSMiddleware': 200,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
}
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,

}
ITEM_PIPELINES = {
   'ineyes_crawler.pipelines.IneyesCrawlerPipeline': 200,
    'ineyes_crawler.pipelines.PubSubPipeline': 230,
   # 'scrapy_redis.pipelines.RedisPipeline': 300,
   # 'ineyes_crawler.pipelines.MongoDBPipeline': 330,
}
SCHEDULER = "ineyes_crawler.scheduler.Seed_Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = 'redis://:LtmJ16w9lZ@139.198.4.56:6379/0'
DEPTH_LIMIT = 10
COOKIES_ENABLED = False
DOWNLOAD_DELAY = random.randint(3,5)
DOWNLOAD_TIMEOUT = 40
REDIRECT_ENABLED = False
SCHEDULER_PERSIST = True  # 不清除，redis序列，这样可以暂停/恢复爬取
LOG_LEVEL= 'DEBUG'


