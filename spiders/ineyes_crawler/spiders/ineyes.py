
from ineyes_crawler.items import IneyesCrawlerItem
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
import  time
from ineyes_crawler.seeds_queue import squeue as sq
from scrapy import signals
from scrapy import Request
import os
from logging.handlers import  RotatingFileHandler
import logging
import threading
from ineyes_crawler.tools.tools import get_host_ip



class Ineyes(RedisCrawlSpider):
    """ 普通文章的通用爬虫"""
    name ='ineyes'
    seed_id = 0
    flag = True  #是否允许加载新种子的标志
    start=[]  #起始链接列表
    UA=0
    isdrag=True   #是否需要多次拖动，False为一次，True为多次
    channel='crawl_data'
    queue_name='wait_queue'
    extra_args={}   #预留的其他参数配置，比如 {'with_cookies':True,'proxy':True}


    def __init__(self, *args, **kwargs):
        """
        初始化爬虫，加载种子配置
        """
        self.node_ip=get_host_ip()
        self.log_init()
        super(Ineyes, self).__init__(*args, **kwargs)



    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        """
        用于为爬虫添加信号处理函数
        """

        spider = super(Ineyes, self).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.inform, signal=signals.spider_idle)  #绑定爬取完毕后的信号处理函数
        spider.signals = crawler.signals
        self.spider = spider
        return spider

    def make_requests_from_url(self,url):  #这个方法只在start——url被调用。
        """
        用于start_urls中的url生成Request
        """

        self.log("请求起始链接：%s"%url)
        self.flag=False
        try:
            request = Request(url, dont_filter=True)  #捕捉start_urls格式错误
        except ValueError as e:
            self.log('url格式错误！%s'%e)
            return None
        return request


    def parse_item(self, response):
        """
        页面解析函数，根据xpath提取表达式在页面响应数据中提取出item数据
        """



        self.log("开始解析 %s 页面数据"%response.url)
        i = IneyesCrawlerItem()
        i.set(self.config['fields'])
        item = ItemLoader(item = i, response = response)  # 使用itemloader 便于添加填充数据规则
        item.add_value("url", response.url)  # 默认增加url
        item.add_value("node_ip", self.node_ip)  # 增加来源节点
        item.add_value("referer", response.request.headers.get('referer').decode('utf-8'))  # 增加来源页面
        self.log("爬取节点为：%s"%self.node_ip)
        if not self.config['fields']:
            i.set(["response"])
            item.add_value("response", str(response.body, "utf-8"))
        else:
            for k, v in self.config['fields'].items():
                if v:
                    self.log("填充字段:%s 规则:%s" % (str(k), v))
                    item.add_xpath(str(k), v)  # 将用户的提取规则逐个增加
        return item.load_item()  # 在load_item中对item进行逐一填充，再返回给管道处理

    def find_seed(self):
        """
        查找种子的方法，在爬虫空闲时被调用，用于查找种子，装配种子信息到爬虫
        """

        self.log("准备提取新的种子任务")
        if self.seed_id and sq.get_all(self.redis_key)!=[]:  #如果还有未处理完的url，不进行新种子提取
            self.log("当前种子未处理完成，暂不进行新种子提取")
            return None
        if sq.get_all(self.queue_name) == []: #队列为空，进行更新
            self.log("种子待爬队列为空，开始更新种子")
            sq.update(self.queue_name)
        self.log('正在等待接收新的爬虫种子')
        self.seed = sq.pop(self.queue_name)  #等待接收从flask传入队列的数据
        if not self.seed:
            return None
        self.config = self.seed[0]
        self.seed_id = str(self.config["id"])
        self.name = "%s:%s" % (self.seed_id, self.config['name'])  # 这是作为redis共享url，item，去重队列的唯一标示
        self.redis_key = self.seed_id + ":start_urls"
        self.log("获取到的种子为：%s" % self.seed)
        self.flag=False
        self.source=self.config['fields'].get("source") or "spider"
        self.start_urls = self.seed[1]
        self.UA=self.config["user_agent_type"]
        self.start=sq.get_all(self.redis_key)
        link_rules = []  # 所需提取的链接规则
        # 增加分页提取规则，用于提取下一页的文章列表页
        if self.config.get("page_rules"):
            for rule in self.config.get("page_rules"):
                self.page_rule = rule
            link_rules.append(Rule(LinkExtractor(allow=(self.page_rule,))))  # 将配置中的规则添加到规则列表
        # 增加提取规则，用于提取详情页，并交给解析函数处理
        if self.config.get("link_rules"):
            for rule in self.config.get("link_rules"):
                self.link_rule = rule
                link_rules.append(Rule(LinkExtractor(allow=(self.link_rule,)), callback='parse_item'))
        self.rules = tuple(link_rules)  # 转化为元组形式的rules属性，用于提取链接。
        self._compile_rules()  # 调用complie_rule对rules中rule进行逐个处理生成Rule实例
    def _build_request(self,rule, link):
        """
        该方法用于根据rule提取到的链接生成Request对象，返回给引擎用于调度下载器下载页面
        重写crawlspider的该方法，增加限制测试类型下的请求生成数量。
        :param rule:
        :param link:
        :return: Requset
        """

        dont_filter= True#进行链接去重
        r = Request(url=link.url, callback=self._response_downloaded,dont_filter=dont_filter)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def log_init(self):
        """
        配置日志设置
        """
        log_path=os.path.abspath('../..') + "/logs/log.log"
        formatter=logging.Formatter("[%(levelname)s][%(asctime)s]%(message)s")
        log_file_handler = RotatingFileHandler(filename=log_path, maxBytes=1500000, backupCount=3)
        log_file_handler.setLevel(logging.INFO)
        log_file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(log_file_handler)


    def inform(self):
        if self.flag:
            self.find_seed()
        else:
            t = threading.Thread(target=self.active)
            t.start()
            return None

    def active(self):  #15秒间隔内收到空闲信号，不激活种子查找。
        self.flag=False
        time.sleep(20)
        self.flag=True




