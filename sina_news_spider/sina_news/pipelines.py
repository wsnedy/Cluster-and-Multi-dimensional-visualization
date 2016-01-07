# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from twisted.enterprise import adbapi
from scrapy import log
import MySQLdb
import MySQLdb.cursors

#用于图片下载并储存的类
class SinaNewsPipeline(ImagesPipeline):

    #对item['image_urls']中的图片网址，用Request请求网页，并下载图片
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url)

    #将下载的图片储存在本地，并且得到图片的本地地址
    def item_completed(self, results, item, info):
        image_paths = ["../images/" + x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

#用于将item中的数据存入Mysql数据库的类
class MySQLStorePipeline(object):
    def __init__(self):
        #连接数据库
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            host = '127.0.0.1',
                                            db = 'newsdb',
                                            user = 'root',
                                            passwd = '314159',
                                            cursorclass = MySQLdb.cursors.DictCursor,
                                            charset = 'utf8',
                                            use_unicode = False
                                            )
    def process_item(self, item, spider):
        #将数据插入数据库
        query = self.dbpool.runInteraction(self._conditional_insert, item, spider)
        #处理错误
        query.addErrback(self._handle_error, item, spider)
        #将item放入query队列中
        query.addBoth(lambda _: item)
        return query

    def _conditional_insert(self, conn, item, spider):
        #如果该条新闻有news_id，则测试该条新闻是不是已经存入数据库，如果没有，执行insert插入的sql语句
        if item.get('news_id'):
            conn.execute("select * from sinanews where news_id = %s", (item['news_id']))
            result = conn.fetchone()
            if result:
                log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
            else:
                #得到该条新闻所属主题的id
                conn.execute("select id from subjects where sub_name = %s", item['sub_name'])
                item['sub_id'] = conn.fetchone()['id']

                #得到该条新闻报道媒体的id
                conn.execute("select id from media where media_name = %s", item['news_media'])
                media_id = conn.fetchone()
                if media_id:
                    item['media_id'] = media_id['id']
                else:
                    conn.execute("""insert into media (media_name) VALUE (%s)""", (item['news_media']))
                    conn.execute("select id from media where media_name = %s", item['news_media'])
                    item['media_id'] = conn.fetchone()['id']

                #将一条新闻的所有需要的信息插入数据库中的sinanews表
                conn.execute("""insert into sinanews (news_id, sub_id, news_url, news_title, news_pubtime, media_id, news_content, news_commentnum,
                  news_commenturl, image_urls, image_paths, news_contentimages) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                             (item['news_id'], item['sub_id'], item['news_url'][0], item['news_title'][0], item['news_pubtime'][0], item['media_id'], item['news_content'][0], item['news_commentnum'], item['news_commenturl'], item['image_urls'][0], item['image_paths'][0], item['news_contentimages']))
                log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def _handle_error(self, e, item, spider):
        log.err(e)