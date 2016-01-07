# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
import re
import json
import urllib
import sys

from sina_news.items import SinaNewsItem

class SinaNewsSpider(CrawlSpider):
    name = "sinanews"
    allowed_domains = ["sina.com.cn"]
    #要爬取的新闻的主题
    subjects = ['mh370', '转基因', '巴黎恐怖袭击', '药品监管', '世界互联网大会', '食品安全', '雾霾', '油价调整', '春运', '二胎政策']
    # print urllib.quote(subjects[0].decode(sys.stdin.encoding).encode('gbk'))
    start_urls = [
        #手动生成网址，得到每个主题在新浪新闻的搜索结果界面。由于新浪新闻的url的中文编码是gbk2312，所以先对主题进行系统编码的解码，然后再进行gbk编码，插入到url中
        "http://search.sina.com.cn/?q=%s&c=news&from=channel&col=&range=all&source=&country=&size=&time=&a=&sort=time&t=3_5_6"%(urllib.quote(sub.decode(sys.stdin.encoding).encode('gbk'))) for sub in subjects
    ]

    rules = [
        #定义爬取规则，利用正则表达式，跟踪爬取符合条件的网址，并用回调函数爬取内容
        Rule(LinkExtractor(allow=(r'&page=(\d+)')), callback= 'parse_search', follow=True)
    ]

    #爬取搜索结果的函数
    def parse_search(self,response):
        sel = Selector(response)
        #通过XPath得到所有的新闻搜索结果
        news = sel.xpath('//div[@class="box-result clearfix"]')
        for eachnews in news:
            #继承items文件中的SinaNewsItem类
            item = SinaNewsItem()
            #通过正则表达式，匹配start_urls网址中的搜索关键词，是在'q='之后，得到该新闻所属的主题
            sub_name = re.match('.*?q=(.*?)&.*',response.url).group(1)
            #通过urllib库中的unquote函数，得到url中的新闻主题，然后先进行gb2312解码，然后进行utf8编码，解决url中文编码问题
            item['sub_name'] = urllib.unquote(sub_name).decode('gb2312').encode('utf8')
            # print item['sub_name']
            item['image_urls'] = eachnews.xpath('div/a/img/@src').extract()
            item['news_url'] = eachnews.xpath('h2/a/@href').extract()
            if(item['news_url']):
                #通过Request请求新闻网页，利用回调函数来爬取新闻网页中所需要的信息，meta用来传递参数，继承之前的item
                yield Request(url=item['news_url'][0],callback=self.parse_news, meta={'item': item})

    #爬取新闻网页的信息
    def parse_news(self,response):
        #继承item
        item = response.meta['item']
        sel = Selector(response)
        item['news_title'] = sel.xpath('//title/text()').extract()
        news_media = sel.xpath('//meta[@name="mediaid"]/@content').extract()
        #由于新浪新闻中，有的新闻没有给出报道媒体，所以爬取不到，并且用extract()得到的都是一个list对象，当没有爬取到媒体时，list为空，不能执行取下标操作，所以赋值为NOMedia
        if news_media:
            item['news_media'] = news_media[0]
        else:
            item['news_media'] = "NoMedia"

        #新浪新闻中，新闻的报道时间有以下三种情况，所以对每个新闻都爬取以下timelist，如果该新闻符合第一种，则得到的后两种为[]，综合三种，就能得到时间。并且包含所有情况
        timelist1 = sel.xpath('//span[@class="time-source"]/text()').re('\d+')[0:3]
        timelist2 = sel.xpath('//span[@id="pub_date"]/text()').re('\d+')[0:3]
        timelist3 = sel.xpath('//span[@class="time"]/text()').re('\d+')[0:3]
        timelist = timelist1 + timelist2 + timelist3
        # print timelist
        #将时间格式化为如2016-01-04的形式
        item['news_pubtime'] = ['-'.join(map(str,timelist))]

        #新浪新闻中，新闻的整体内容有以下两种情况，和上面的时间一样，综合两种，能包含所有情况
        news_content1 = sel.xpath('//div[@id="artibody"]').extract()
        news_content2 = sel.xpath('//div[@class="mainContent"]').extract()
        item['news_content'] = news_content1 + news_content2

        #由于新闻内容有以上两种情况，所以可以知道，新闻内容中的图片也有以下两种情况，综合两种，可以包含所有情况
        news_contentimg1 = sel.xpath('//div[@id="artibody"]//img/@src').extract()
        news_contentimg2 = sel.xpath('//div[@class="mainContent"]//img/@src').extract()
        contentimg_list = news_contentimg1 + news_contentimg2
        #将照片地址之间用逗号连接
        item['news_contentimages'] = ','.join(contentimg_list)

        #每条新浪新闻，由channel和newsid共同决定，新闻中的这两条信息分别有以下两种情况，综合两种
        channel1 = sel.xpath('//script').re('channel:.*\'(.*)\'')   #如 channel: 'sh'
        channel2 = sel.xpath('//script').re('channel:.*\"(.*)\"')   #如 channel: "sh"
        channel = channel1 + channel2
        newsid1 = sel.xpath('//script').re('newsid:.*\'(.*)\'')     #如 newsid: 'comos-fxncyar6113773'
        newsid2 = sel.xpath('//script').re('newsid:.*\"(.*)\"')     #如 newsid: "comos-fxncyar6113773"
        newsid = newsid1 + newsid2
        #有的新闻找不到新闻id，这种情况就舍弃这条新闻
        try:
            item['news_id'] = newsid[0]
        except IndexError:
            pass

        #通过上面的channel和newsid，我们可以手动生成该条新闻评论的网址（通过firebug抓包得到新闻评论网址，然后总结规律）
        cmturl = "http://comment5.news.sina.com.cn/page/info?format=json&channel=%s&newsid=%s&page_size=200"%(channel[0],newsid[0])
        item['news_commenturl'] = cmturl

        #通过Request请求新闻评论的网页，利用回调函数来得到所需要的新闻评论数
        yield Request(url=cmturl,callback=self.parse_commentnum,meta={'item': item})

    #通过打开新闻评论网址，可以发现得到的是json文件，所以调用python的json模块来解析json，得到所需要的新闻评论数
    def parse_commentnum(self,response):
        data = json.loads(response.body_as_unicode())
        item = response.meta['item']
        #有时候请求网页会失败，得不到数据，这种情况，我们直接给评论数赋值为0
        try:
            item['news_commentnum'] = data["result"]["count"]["total"]
        except KeyError:
            item['news_commentnum'] = 0
        return item
