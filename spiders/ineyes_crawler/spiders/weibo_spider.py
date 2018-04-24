from ineyes_crawler.spiders.ineyes import Ineyes
from ineyes_crawler.items import IneyesCrawlerItem
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import Rule
from scrapy.http import HtmlResponse
from ineyes_crawler.seeds_queue import squeue as sq
from pymongo import MongoClient
import redis
from scrapy import Request
from lxml import etree
import time
from ineyes_crawler.seeds_mysql import SeedsMysql
import requests
import ineyes_crawler.tools as tools
import urllib
from ineyes_crawler.config import redis_config


class Weibo_spider(Ineyes):
    """
    微博爬虫
    """
    name = 'weibo_spider'
    isdrag=False
    channel='crawl_data'
    queue_name = 'weibo_queue_realtime'
    extra_args = {'with_cookies': True}

    def __init__(self):
        """
        初始化连接redis，mongo
        """
        super(Weibo_spider, self).__init__()
        self.r = redis.Redis(host=redis_config['redis_host'], port=redis_config['redis_port'],password=redis_config['redis_password'])
        self.update_queue()
        # self.nojs=True



    def update_queue(self):
        """
        提取链接装配种子放入队列

        """
        mq = SeedsMysql()
        seeds = mq.get_seeds(-101)  # 得到装配好的状态为-101的种子，即为爬虫种子母体
        mq.close()
        for seed in seeds:
            platform = seed[0]['fields']['source']
            print(seed)
            key = "%s:weibo_start_urls_realtime" % platform
            print('等待url中....')
            url=sq.pop('crawl_weibo')
            print('获得url %s'%url)
            self.r.lpush(key, url)  #载入start_url
            self.r.lpush(self.queue_name, seed)
            self.r.expire(self.queue_name, 3600)
            self.log('种子装载成功')



    def find_seed(self):
        """
              查找种子的方法，在爬虫空闲时被调用，用于查找种子，装配种子信息到爬虫
              """

        self.log("准备提取新的种子任务")
        if self.seed_id and sq.get_all(self.redis_key) != []:  # 如果还有未处理完的url，不进行新种子提取
            self.log("当前种子未处理完成，暂不进行新种子提取")
            return None
        if sq.get_all(self.queue_name) == []:  # 队列为空，进行更新
            self.log("种子待爬队列为空，开始更新种子")
            self.update_queue()

        self.log('正在等待接收新的爬虫种子')
        self.seed = sq.pop(self.queue_name)
        if not self.seed:
            return None
        self.config = self.seed[0]
        self.source = self.config['fields']['source']
        self.name = self.config['name']+':weibo'  # 这是作为redis共享url，item，去重队列的唯一标示
        self.seed_id = str(self.config["id"])
        self.redis_key = self.source + ":weibo_start_urls_realtime"
        self.log("获取到的种子为：%s" % self.seed)
        self.flag = False
        self.start_urls = self.seed[1]
        self.UA = self.config["user_agent_type"]
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


    def parse_item(self, response):
        """
        页面解析函数，根据xpath提取表达式在页面响应数据中提取出item数据
        """

        self.log("开始解析 %s 文章页面数据" % response.url)
        self.log("爬取节点为：%s" % self.node_ip)
        for i in response.xpath("//*[@action-type='feed_list_item']"):
            item = IneyesCrawlerItem()
            item.set(self.config['fields'])
            for k, v in self.config['fields'].items():
                if v:
                    self.log("填充字段:%s 规则:%s" % (str(k), v))
                    item[k]=i.xpath(v).extract() if i.xpath(v) else ""
            item["url"]=[response.url]  # 默认增加url
            print('当前url%s'%item['url'])
            yield item


    # def parse_item(self, response):
    #     """
    #     页面解析函数，根据xpath提取表达式在页面响应数据中提取出item数据
    #     """
    #
    #     self.log("开始解析 %s 文章页面数据" % response.url)
    #
    #
    #     i = IneyesCrawlerItem()
    #     i.set(self.config['fields'])
    #     item = ItemLoader(item=i, response=response)  # 使用itemloader 便于添加填充数据规则
    #     item.add_value("url", response.url)  # 默认增加url
    #     item.add_value("node_ip", self.node_ip)  # 增加来源节点
    #     self.log("爬取节点为：%s" % self.node_ip)
    #     for k, v in self.config['fields'].items():
    #         if v:
    #             self.log("填充字段:%s 规则:%s" % (str(k), v))
    #             item.add_xpath(str(k), v)  # 将用户的提取规则逐个增加
    #     return item.load_item()  # 在load_item中对item进行逐一填充，再返回给管道处理
    #
    #
    # def parse_name(self, response):
    #     self.log("开始解析 %s 用户id提取页面数据" % response.url)
    #     # response.xpath('//a[contains(@href, "from=")]/@href').re(r'Name:\s*(.*)')
    #
    #     # weibo.com/sohutv?refer_flag
    #     # link=response.xpath('//a[contains(@href, "from=")]/@href')
    #     names = response.xpath('//a[contains(@href, "refer_flag")]/@href').re(r'weibo.com/(.*)\?refer')
    #     names=set(names)
    #     for name in names:
    #         return self.get_weibo_by_name(name)
    #
    # def get_weibo_by_name(self,name):
    #     c = requests.get('https://weibo.cn/{}'.format(name)).content
    #     selector = etree.HTML(c)
    #     try:
    #         url= selector.xpath("//*[@class='cc']/@href")[0]
    #     except Exception as e:
    #         self.log(e)
    #         return False
    #     # for url in urls[0]:
    #     content = requests.get(url).content
    #     request = Request(url, dont_filter=False)
    #     response=HtmlResponse(url, encoding='utf-8', body=content, request=request)
    #     return self.parse_item(response)






