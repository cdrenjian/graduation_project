from graduation_project.spiders.ineyes_crawler.tools.weibo_cookies_pool import Cookies_pool
from graduation_project.web_app.redis_queue import Queue
import requests
from lxml import etree
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
import re
import redis
import json



redis_config={
'redis_host':"139.198.4.56",
'redis_port':6379,
'redis_password':'LtmJ16w9lZ',
'timeout':100,
}


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)



c=Cookies_pool()
main_url='https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&refer_flag=0000015010_&from=feed&loc=nickname&is_all=1&pagebar=1&pl_name=Pl_Official_MyProfileFeed__21&id=100505{0}&script_uri={1}&feed_type=0&page=1&domain_op=100505&__rnd=1524557007862'

class Fast_crawler(object):
    def __init__(self):
        self.c = Cookies_pool()
        self.main_url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&refer_flag=0000015010_&from=feed&loc=nickname&is_all=1&pagebar=1&pl_name=Pl_Official_MyProfileFeed__21&id=100505{0}&script_uri={1}&feed_type=0&page={2}&domain_op=100505&__rnd=1524557007862'
        self.redis_client = redis.Redis(host=redis_config['redis_host'], port=redis_config['redis_port'],password=redis_config['redis_password'])
    def crawl_by_home(self,url):
        cookies=c.get_cookies()
        r_cookies = {}
        for cookie in cookies:
            r_cookies[cookie['name']] = cookie['value']
        r = requests.get('https://weibo.com/u/2035694401/home?wvr=5&lf=reg', cookies=r_cookies)
        if "我的首页" in r.text:
            logging.info('cookies有效！验证成功')
        json_data=requests.get(url,cookies=r_cookies).json()
        content=json_data["data"]
        self.html_parse(content)

    def html_parse(self,html_data):
        selector = etree.HTML(html_data)
        for i in selector.xpath("//*[@node-type='feed_list_content']"):
            content=i.xpath('string(.)').strip()
            author=i.get('nick-name')
            publish_date=i.getparent().xpath('.//*[@class="WB_from S_txt2"]/a[1]/text()')[0]
            logging.info('作者：{} \n 内容：{} \n 发布时间:{} \n'.format(author,content,publish_date))
            meta_data={'author':author,'content':content,'publish_date':publish_date}
            self.redis_client.publish('weibo_gp',json.dumps(meta_data))





    #https://weibo.com/u/1953993237?refer_flag=1005055014_
    def parse_home_url(sefl,home_url):
        http_headers = {'Accept': '*/*', 'Connection': 'keep-alive',
                        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 3.0.1; fr-fr; A500 Build/HRI66) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'}

        rs = requests.get(home_url, headers=http_headers, timeout=10)
        now_url=rs.url
        print(now_url)
        try:
            user_id=now_url.split('u/')[1][:10]
        except:
            user_id=now_url.split('p/')[1].replace('100505','')
        uri="/u/{}".format(user_id)
        print(user_id)
        print(uri)
        return user_id,uri


    def start_crawl(self,url):
        user_id, uri = self.parse_home_url(url)
        for page in range(1,4):
            req_url = self.main_url.format(user_id, uri,page)
            print(req_url)
            self.crawl_by_home(req_url)

if __name__=='__main__':
    f=Fast_crawler()
    f.start_crawl('https://weibo.com/cctvwzn?from=feed&loc=nickname')
    # queue=Queue()
    # while True:
    #     logging.info('等待任务中...')
    #     home_link = queue.pop()
    #     logging.info('获得新任务：%s'%home_link)
    #     f.start_crawl(home_link)
