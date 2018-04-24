# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class IneyesCrawlerItem(scrapy.Item):
    """
    用于定义item数据字段
    """

    id = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()  #数据来源，默认为spider
    timestamp = scrapy.Field()
    node_ip=scrapy.Field()
    referer=scrapy.Field()
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def set(self, fields):
        """
        用来动态添加自定义属性
        """
        for field in fields:
            self.__setattr__(field, scrapy.Field())
            self.fields[field] = scrapy.Field()
