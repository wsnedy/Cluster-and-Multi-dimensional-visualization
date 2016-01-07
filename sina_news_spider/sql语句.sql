CREATE DATABASE newsdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE subjects (
    id INT AUTO_INCREMENT,
    sub_name VARCHAR(255),
    PRIMARY KEY (id)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE media (
    id INT AUTO_INCREMENT,
    media_name VARCHAR(255),
    PRIMARY KEY (id)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;


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

insert into subjects (sub_name) values ('mh370'), ('转基因'), ('食品安全'), ('巴黎恐怖袭击'), ('药品监管'), ('世界互联网大会'), ('雾霾'), ('油价调整'), ('春运'), ('二胎政策');
