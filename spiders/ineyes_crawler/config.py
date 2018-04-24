



#---------redis config---------
redis_config={
'redis_host':"139.198.4.56",
'redis_port':6379,
'redis_password':'LtmJ16w9lZ',
'timeout':100,
}

mongo_config={

}





#重点账户的文章爬取规则和自媒体资料更新规则
focus_article_xpath = {

    'toutiao':{'fields':{"author":"//*[@class='name']|/html/body/div/div[2]/div[2]/div[1]/div[1]/span[last()-1]","author_home":"//*[@class='media-user']/@href|/html/body/div/div[2]/div[3]/div[1]/div/div/div/a/@href","comment_count":"//*[@id='comment']/div[1]/em","content":"/html/body/div/div[2]/div[2]/div[1]/div[2]","publish_date":"/html/body/div/div[2]/div[1]/div/div/div[2]/div[2]/div[1]/span|/html/body/div/div[2]/div[2]/div[1]/div[1]/span[last()]","source":"toutiao","title":"/html/body/div/div[2]/div[1]/div/div/div[2]/div[1]/h2|/html/body/div/div[3]/div[1]/div[3]/h2|/html/body/div/div[2]/div[2]/div[1]/h1","reader_count":"/html/body/div/div[3]/div[1]/div[3]/div[3]/div[2]/span/em","like_count":"//*[@class='digg']","dislike_count":"//*[@class='bury']","original":"//*[@class='original']"},'link_rules':['group']},
    'ifeng':{'fields':{"title":"//*[@class='yc_tit']/h1","author":"/html/body/div[3]/div[1]/p/a[2]","publish_date":"/html/body/div[3]/div[1]/p/span","content":"//*[@class='yc_con_txt']","comment_count":"//*[@class='w-num']","reader_count":"","like_count":"","dislike_count":"","source":"ifeng","author_home":"","original":""},"link_rules":["wemedia.shtml"]},
     'baijia':{'fields':{"title":"//*[@id='content_wrapper']/header/h1|//*[@id='content']/div[1]/div[2]/h1","content":"//*[@id='content_wrapper']/div/div[1]","author":"//*[@id='content_wrapper']/header/section/h3/div[2]/a/div","author_home":"//*[@id='content']/aside/div/div[1]/div[1]/div/div[1]/a/@href","reader_count":"//*[@id='content']/article/div/article/section[1]/div/span[3]","publish_date":"//*[@id='content_wrapper']/header/section/h3/div[2]/div/span[2]","source":"baijia","comment_count":"","like_count":"//*[@class='like']","dislike_count":"//*[@class='dislike']","original":""},'link_rules':["newspage/data"]},
     'yidian':{'fields':{"title":"/html/body/div[2]/div[1]/h2","content":"/html/body/div[2]/div[1]/div[2]","author":"/html/body/div[2]/div[1]/div[1]/a","author_home":"/html/body/div[2]/div[1]/div[1]/a/@href","publish_date":"//*[@class='meta']/span[last()-1]","reader_count":"","comment_count":"","like_count":"","dislike_count":"","original":"//*[@class='wm-copyright']","source":"yidian"},'link_rules':['article']},
    'neteasy':{'fields':{"title":"//*[@id='contain']/div/div[2]/h2","content":"//*[@id='content']","author":"/html/body/div[4]/div/div[1]/div[2]/div[1]/h4","author_home":"","publish_date":"//*[@id='contain']/div/div[2]/div[1]/p/span[1]","reader_count":"","comment_count":"//*[@id='contain']/div/div[2]/div[1]/span/span/a","like_count":"","dislike_count":"","source":"neteasy","original":""},"link_rules":["/v2/article/detail"]},
    'time':{'fields':{"title":"//*[@id='title']","content":"//*[@id='content-text']","author":"//*[@class='cite']","author_home":"//*[@class='author']/@href","reader_count":"//*[@class='read-count']","publish_date":"//*[@class='time']","comment_count":"//*[@id=\"article-info-qh\"]/div/div/div/em","source":"time","like_count":"","dislike_count":"","original":""},"link_rules":["item.btime.com"]},
    'sohu':{'fields':{'title':"//*[@id='crumbsBar']/div/div[1]/h2","content":"//*[@id='content']/div[1]/div[1]/div[2]/p/span[2]","author":"//*[@id='content']/div[1]/div[1]/div[2]/div[1]/p/a[1]","author_home":"//*[@id='content']/div[1]/div[1]/div[2]/div[1]/p/a[1]/@href","reader_count":"//*[@id='playtoolbar']/div[8]/span/em/i","publish_date":"//*[@id='playtoolbar']/div[9]/span/em/i","comment_count":"//*[@id='commList']/div[1]/text()","source":"sohu","like_count":"//*[@id='playtoolbar']/div[1]/a/em/i","dislike_count":"//*[@id='playtoolbar']/div[2]/a/em/i","original":""},"link_rules":["us/"]},

}
focus_account_xpath ={
    'toutiao':{"avatar_url":"//*[@id='J_section_0']/a/div[1]/img/@src","reader_count":"","article_count":""},
     'ifeng':{"avatar_url":"//*[@class='intro_logo']/@src","reader_count":"","article_count":""},
     'baijia':{"avatar_url":"//*[@class='avatar']//@data-src","reader_count":"","article_count":""},
    'yidian':{"avatar_url":"//*[@class='channel-image-box']//@src","reader_count":"","article_count":""},
    'neteasy': {"avatar_url": "//*[@class='colum_info']//@src", "reader_count": "", "article_count": "/html/body/div[4]/div/div[1]/div[2]/div[2]/div[1]/p[1]/text()"},
    'sohu':{"avatar_url":"//*[@id='user_avatar']/@src","reader_count":"//*[@id='user_info']/div[2]/ul/li[1]/span[1]/text()","article_count":"//*[@id='videos_list_num']/text()"},

}

#普通账户的资料更新规则
wedia_account_xpath = {
     'neteasy': {"avatar_url": "/html/body/div[4]/div/div[1]/div[2]/div[1]/img/@src",
                  'article_count': '/html/body/div[4]/div/div[1]/div[2]/div[2]/div[1]/p[1]'},
    'toutiao': {"avatar_url": "//*[@id='wrapper']/div[1]/div/a/img"},
     'baijia': {"avatar_url": "//*[@id='content']/div[1]/div[1]/div[1]/img/@src",
                "article_count": "//*[@class='publish-total']/span[1]",
              "reader_count": "//*[@id='articleList']/div[2]/span[2]"},
     'yidian': {"avatar_url": "//*[@id='js-main']/div[1]/div[1]/div/div/div[1]/img/@src"},
     'sohu': {"avatar_url": "//*[@class='profile_all']/img/@src", "article_count": "//*[@class='data_acticle']/p[1]",
            "reader_count": "//*[@class='data_read']/p[1]"},
    'time': {"avatar_url": "//*[@class='avator']/img/@src", "article_count": "",
        "reader_count": ""},

}

#用于搜索关键词的start_url
so_url={
#'uc':'https://news.uc.cn/search?kw={}',
'baijia':'https://www.baidu.com/s?wd={}%20site%3Abaijia.baidu.com&pn=1',
'ifeng':'https://www.baidu.com/s?wd={}%20site%3Aifeng.com&pn=1',
'neteasy':'https://www.so.com/s?q={}+site%3A3g.163.com&pn=1',
'qq':'https://www.sogou.com/tx?query={}+site%3Axw.qq.com&page=1',
'sohu':'http://search.sohu.com/?keyword={}&source=article&queryType=edit&ie=utf8',
'time':'https://www.so.com/s?q={}+site%3Aitem.btime.com&pn=1',
'toutiao':'https://www.toutiao.com/search/?keyword={}',
'yidian':'http://www.yidianzixun.com/channel/w/{}'

}