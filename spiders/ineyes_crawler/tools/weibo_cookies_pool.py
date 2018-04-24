from selenium import webdriver
from time import sleep
import logging
import json
import redis
import requests
from graduation_project.spiders.ineyes_crawler.config import redis_config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
chromePath = r'/Users/tomato/renjian/webdriver/chromedriver'



class Cookies_pool(object):
    def __init__(self):
        self.r = redis.Redis(host=redis_config['redis_host'], port=redis_config['redis_port'],password=redis_config['redis_password'],decode_responses=True)

    def add_new_cookies(self,username,password):
        """ selenium 模拟登录 获取cookies"""
        #d = webdriver.Chrome(executable_path=chromePath)
        d=webdriver.PhantomJS()
        wb_url = 'https://weibo.com/'
        d.get(wb_url)
        sleep(8)
        d.set_window_size(1124, 850)
        d.find_element_by_xpath('//*[@id="loginname"]').send_keys(username)
        d.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys(password)
        sleep(10)  # 手动输入验证码
        d.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
        sleep(10)  # 等待Cookies加载
        cookies = d.get_cookies()
        self.add_cookies(cookies)
        d.quit()

    def add_cookies(self, selenium_cookies):
        """cookies 入队"""
        self.r.lpush('weibo_cookies',json.dumps(selenium_cookies))

    def valid(self,cookies):
        """ 验证cookies是否有效 """
        if not cookies:
            logging.info('cookies池耗尽，无可用cookies')
            raise ValueError
        r_cookies={}
        for cookie in cookies:
            r_cookies[cookie['name']]=cookie['value']
        r=requests.get('https://weibo.com/u/2035694401/home?wvr=5&lf=reg',cookies=r_cookies)
        if "我的首页" in r.text:
            logging.info('cookies有效！验证成功')
            return True
        else:
            logging.info('cookies失效！验证失败')
            return False

    def get_cookies(self):
        """ 从队列中获取有效的cookies"""
        cookies = self.r.rpop('weibo_cookies')
        if cookies:
            cookies=json.loads(str(cookies).replace('\'','\"'))
            while not self.valid(cookies):          #一直取cookies，直到验证成功！
                cookies = self.r.rpop('weibo_cookies')
                cookies = json.loads(str(cookies).replace('\'', '\"'))
                logging.info('获取到cookies')
            self.r.lpush('weibo_cookies',json.dumps(cookies))   #可用cookies重新入队
            return cookies
        logging.info('cookies耗尽')
        self.add_new_cookies('13550331559','87280932.')
        return  self.get_cookies()




if  __name__=="__main__":
    c=Cookies_pool()
    c.add_new_cookies('13550331559','87280932.')




