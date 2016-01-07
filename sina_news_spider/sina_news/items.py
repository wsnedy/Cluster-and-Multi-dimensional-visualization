# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    #定义对每条新闻要爬取的内容，为每种内容设置一个保存的item对象，item提供了类似于字典的API以及用于声明可用字段的语法
    sub_name = scrapy.Field()               #每条新闻所属的主题
    sub_id = scrapy.Field()                 #每条新闻所属主题的ID
    news_id = scrapy.Field()                #每条新闻的ID
    news_url = scrapy.Field()               #每条新闻的网址
    news_title = scrapy.Field()             #每条新闻的新闻标题
    news_pubtime = scrapy.Field()           #每条新闻的报道时间
    news_media = scrapy.Field()             #报道该条新闻的媒体
    media_id = scrapy.Field()               #报道该条新闻的媒体的ID
    news_content = scrapy.Field()           #每条新闻的整体内容
    news_contentimages = scrapy.Field()     #每条新闻的内容中的图片地址
    news_commentnum = scrapy.Field()        #每条新闻的评论数
    news_commenturl = scrapy.Field()        #每条新闻评论的地址
    image_urls = scrapy.Field()             #每条新闻的第一张图片的地址
    images = scrapy.Field()                 #新闻图片
    image_paths = scrapy.Field()            #每条新闻的第一张图片的本地地址
