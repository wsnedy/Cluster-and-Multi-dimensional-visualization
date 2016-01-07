# -*- coding: utf-8 -*-
#comment.py主要是用于爬取每条新闻的200条评论
#大致的流程为：
#首先连接数据库，从数据库中sinanews表格中选取每条新闻的评论地址，
#然后利用requests模块，请求评论地址，得到一个json格式的文件，
#解析json文件，从中得到每条评论的信息，
#将得到的每条评论存入数据库中的sinacomment表格
#评论地址response返回的json文件格式可以参考下面的网址
#http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=sh&newsid=comos-fxncyar6113773&page_size=20

import MySQLdb
import requests
import json

db = MySQLdb.connect("127.0.0.1","root","314159","newsdb", charset="utf8")
cursor = db.cursor()
cursor.execute("SELECT news_commenturl from sinanews")
data = cursor.fetchall()
for urllist in data:
    for url in urllist:
        try:
             r = requests.get(url)
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.TooManyRedirects:
            continue
        except requests.exceptions.RequestException as e:
            print e
            continue

        try:
            cmtdata = json.loads(r.text)
        except ValueError:
            continue
        # print cmtdata["result"]
        try:
            cmtlist = cmtdata["result"]["cmntlist"]
            for cmt in cmtlist:
                #把得到的信息里的'去掉
                news_id =''.join(cmt['newsid']).replace("'",'')
                area = ''.join(cmt['area']).replace("'",'')
                cmt_content = ''.join(cmt['content']).replace("'",'')
                nickname = ''.join(cmt['nick']).replace("'",'')
                agree_count = ''.join(cmt['agree']).replace("'",'')
                # print news_id
                # print area
                # print cmt_content
                # print nickname
                # print agree_count
                # news_id = cmt['newsid'].encode("utf8")
                # area = cmt['area'].encode("utf8")
                # cmt_content = cmt['content'].encode("utf8")
                # nickname = cmt['nick'].encode("utf8")
                # agree_count = cmt['agree'].encode("utf8")
                # print news_id + ",", area + ",", cmt_content + ",", nickname + ",", agree_count
                try:
                    #由于评论，昵称可能会有"或者'等等符号，会影响插入，如果不满足以下这种形式的，就把这条评论去掉
                    cursor.execute("""insert into sinacomment (news_id, area, cmt_content, nickname, agree_count) VALUES ('%s', '%s', '%s', '%s', '%s')"""%(news_id, area, cmt_content, nickname, agree_count))
                except:
                    continue
                db.commit()
                # test = cursor.execute("SELECT news_id from sinacomment")
                # print cursor.fetchall()
                print "insert success"
        except KeyError:
            continue

