对新闻数据的爬取并把新闻数据存入数据库
数据源： 新浪新闻
整个运行过程：
1.打开数据库，运行sql语句文件中的sql代码，创建数据库以及数据表格
2.更改sina_news文件夹中pipeline文件，将其中的链接数据库的host,用户名，密码，更改成自己的。
3.进入sina_news/sina_news/spiders，在此处打开cmd，运行"scrapy crawl sinanews"语句（前提是已经安装了scrapy）
4.待sinanews爬虫爬取完成之后，运行comment.py文件


分为以下几个部分详细介绍整个过程：

1.数据库结构
		数据库中总共含有4个表格，subjects, media, sinanews, sinacomment
		建立表格的sql语句为：
		subjects:
		
		CREATE TABLE subjects (
		id INT AUTO_INCREMENT,
		sub_name VARCHAR(255),
		PRIMARY KEY (id)
		)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
		
		media:
		
		CREATE TABLE media (
		id INT AUTO_INCREMENT,
		media_name VARCHAR(255),
		PRIMARY KEY (id)
		)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
		
		sinanews:
		
		CREATE TABLE sinanews (
		news_id VARCHAR(255) NOT NULL,
		sub_id INT,
		media_id INT,
		news_url VARCHAR(255) NOT NULL,
		news_title VARCHAR(255) NOT NULL,
		news_pubtime DATE,
		news_content TEXT,
		news_commentnum INT,
		news_commenturl VARCHAR(255),
		image_urls VARCHAR(255),
		image_paths VARCHAR(255),
		news_contentimages TEXT,
		PRIMARY KEY (news_id),
		INDEX (sub_id),
		FOREIGN KEY (sub_id)
        REFERENCES subjects (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
		INDEX (media_id),
		FOREIGN KEY (media_id)
        REFERENCES media (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
		)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
		
		可以看出sinanews表格中有两个外键，一个是与subjects中的主题id链接，一个是与media中的媒体id链接，
		使用外键能使得表格数据看起来更加有序，并且可以防止随意插入数据。
		
		sinacomment:
		
		CREATE TABLE sinacomment (
		id INT AUTO_INCREMENT,
		news_id VARCHAR(255),
		area 	VARCHAR(255),
		cmt_content text,
		nickname VARCHAR(255),
		agree_count int,
		PRIMARY KEY (id),
		FOREIGN KEY (news_id)
        REFERENCES sinanews (news_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
		)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
		
		sinacomment中也有外键，与sinanews中的news_id链接，使得可以得到该条评论是哪条新闻的。
	
2.scrapy爬虫
		利用CrawlSpider类，以及Rule规则，依次爬取新浪新闻搜索界面，新闻界面，以及新闻评论数
		关于scrapy的具体知识，可以参考官方文档：http://scrapy-chs.readthedocs.org/zh_CN/latest/topics/spiders.html
		然后利用pipeline对item数据进行处理，下载图片，得到图片的本地地址，将数据存入数据库。
		关于scrapy对图片的下载，可以参考官方文档： http://scrapy-chs.readthedocs.org/zh_CN/latest/topics/images.html
		有关scrapy将数据存入Mysql的实例，可以参考： http://www.cnblogs.com/rwxwsblog/p/4572367.html


3.comment.py
		首先连接数据库，从数据库中sinanews表格中选取每条新闻的评论地址，
		然后利用requests模块，请求评论地址，得到一个json格式的文件，
		解析json文件，从中得到每条评论的信息，
		将得到的每条评论存入数据库中的sinacomment表格
		评论地址response返回的json文件格式可以参考下面的网址
		http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=sh&newsid=comos-fxncyar6113773&page_size=20
		
		python连接数据库可以参考：
		http://www.runoob.com/python/python-mysql.html

		
4.主题乱码问题
		在手动生成新浪搜索结果的url时，要知道url中的编码是什么，用urllib.quote编码时，得预先将关键词编码成gbk才能用（关于如何知道
		是url中的中文编码是gb2312，可以用chardet模块），
		还有要注意的是，在得到新闻的subject时，用urllib.unquote()解码，得到中文是用gb2312编码的，而我们的编码是utf8，所以得先用gb2312
		解码，再用utf8编码，才不会得到乱码。
		可以在开始时用python的chardet模块判断网页的编码，具体可以参考：http://www.pythonclub.org/modules/chardet
		