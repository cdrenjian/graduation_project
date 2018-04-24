from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from ineyes_crawler.useragent import agents,m_agents
from scrapy.http import HtmlResponse
from selenium import webdriver
import time
import random
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
import requests
from ineyes_crawler.tools.tools import get_proxy
import random
from PIL import Image
from ineyes_crawler.tools.ruokuai_verify import rc
from ineyes_crawler.tools.weibo_cookies_pool import Cookies_pool

# service_args = []
# # service_args= get_proxy()  #预留的IP代理参数
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# agent = random.choice(agents)
# dcap["phantomjs.page.settings.userAgent"] = (agent)  # 设置user-agent请求头
# #dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
# driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_args)
# # driver = webdriver.Chrome(executable_path='/Users/tomato/renjian/webdriver/chromedriver', desired_capabilities=dcap,
# #                          service_args=service_args)
# driver.set_page_load_timeout(30)

class SubUserAgentMiddleware(UserAgentMiddleware):
    """
    用于添加随机的UA
    """

    def process_request(self, request, spider):
        if spider.UA==1:     #1为移动UA ，0为pcUA
            agent = random.choice(m_agents)
            spider.log("当前采用移动端UA")
        else:
            agent = random.choice(agents)
            spider.log("当前采用PC端UA")
        request.headers["User-Agent"] = random.choice(agent)





def not_js(request):
    r=requests.get(request.url)
    response = HtmlResponse(request.url, encoding='utf-8', body=r.content, request=request)
    return response

def has_iframe(driver):
    try:
        driver.find_element_by_tag_name("iframe")
        print('------切换到iframe-------')
    except:
        print('------不包含iframe-------')
        return False
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    return True


class PhantomJSMiddleware(object):
    """
    用于模拟浏览器访问，执行js动作，生成真实的页面响应并返回
    """

    @classmethod
    def driver_init(cls):
        """
        创建浏览器实例
        :return:
        """
        service_args=[]
        #service_args= get_proxy()  #预留的IP代理参数
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        agent = random.choice(agents)
        dcap["phantomjs.page.settings.userAgent"] = (agent)  # 设置user-agent请求头
        #dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
        driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_args)
        #driver = webdriver.Chrome(executable_path='/Users/tomato/renjian/webdriver/chromedriver',desired_capabilities=dcap,service_args=service_args)
        driver.set_page_load_timeout(30)
        return driver

    @classmethod
    def process_request(cls, request, spider):
        if hasattr(spider,'nojs'):   #部分爬虫爬取页面为静态 无须js加载处理
            response=not_js(request)
            return response
        driver=cls.driver_init()
        if spider.extra_args.get('with_cookies') == True:  #是否添加cookies ，目前cookies池只有微博cookies
            driver.get(request.url)
            driver.delete_all_cookies()
            c=Cookies_pool()
            cookies=c.get_cookies()   #添加cookies
            for cookie in cookies:
                if cookie['domain'][0] != '.':
                    cookie['domain'] = '.' + cookie['domain']
                driver.add_cookie(cookie)
            # driver.get('https://weibo.com/u/2035694401/home?wvr=5&lf=reg')
            # if '我的首页' in driver.title:
            #     spider.log('cookies 添加成功')
        try:
            driver.get(request.url)
            time.sleep(3)
            # has_iframe(driver)  #如果有iframe，则切换至iframe
        except TimeoutException as e:
            driver.quit()
            spider.log("模拟浏览器访问页面超时")
            spider.log("切换至静态页面处理")
            response=not_js(request)
            return response
        if spider.isdrag and request.url in spider.start:
            for i in range(random.randint(2,5)): #随机执行js拉动次数
                print('拉动一次')
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)  # 等待JS执行
        #---------填写验证码------------
        if 'weibo' in request.url:
            spider.log('检查是否出现验证码')
            try:
                # img=driver.find_element_by_xpath("//*[@class='code_img']/img")
                # code_url=img.get_attribute('src')
                # spider.log('验证码url：%s'%code_url)
                driver.save_screenshot('./code.png')
                img = driver.find_element_by_xpath("//*[@class='code_img']/img") #定位验证码位置
                #------------获得验证码图片大小及位置，定点截取
                left = img.location['x']
                top = img.location['y']
                right = img.location['x'] + img.size['width']
                bottom = img.location['y'] + img.size['height']
                time.sleep(5)
                spider.log('--------------------------------')
                im = Image.open('./code.png')
                im = im.crop((left, top, right, bottom))
                im.save('./code.png')
                with open('./code.png','rb') as f:
                    img_s=f.read()
                code=rc.verify_weibo(img_s)
                if code:
                    spider.log('识别结果:%s'%code)
                else:
                    spider.log('验证码识别失败')
                    return False
                driver.find_element_by_xpath('//*[@id="pl_common_sassfilter"]/div/div/div/div/div[1]/span[1]/input').send_keys(code)
                time.sleep(3)
                driver.find_element_by_xpath('//*[@id="pl_common_sassfilter"]/div/div/div/div/div[3]/a').click()
                time.sleep(5)
            except Exception as e:
                time.sleep(5)
                spider.log('异常:%s'%e)
        # try:
        #     driver.find_element_by_link_text('下一页').click()     #翻页
        # except Exception as e:
        #     spider.log(e)
        #     pass
        content = driver.page_source.encode('utf-8')
        spider.log("请求页面成功： %s %s"%(driver.title,driver.current_url))
        driver.quit()
        response=HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        return response


def verify(driver,img_xpath,input_xpath,submit_xpath):  #todo 通用的验证码识别 兼容微博，微信
    try:
        driver.save_screenshot('./code.png')
        img = driver.find_element_by_xpath("//*[@class='code_img']/img")  # 定位验证码位置
        # ------------获得验证码图片大小及位置，定点截取
        left = img.location['x']
        top = img.location['y']
        right = img.location['x'] + img.size['width']
        bottom = img.location['y'] + img.size['height']
        time.sleep(5)
        im = Image.open('./code.png')
        im = im.crop((left, top, right, bottom))
        im.save('./code.png')
        with open('./code.png', 'rb') as f:
            img_s = f.read()
        code = rc.verify_weibo(img_s)
        if code:
            print('识别结果:%s' % code)
        else:
            print('验证码识别失败')
            return False
        driver.find_element_by_xpath('//*[@id="pl_common_sassfilter"]/div/div/div/div/div[1]/span[1]/input').send_keys(
            code)
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="pl_common_sassfilter"]/div/div/div/div/div[3]/a').click()
        time.sleep(5)
    except Exception as e:
        time.sleep(5)
        print('异常:%s' % e)


