# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class SinanewsPipeline(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        mdb = self.client['1012005543']
        self.collection = mdb['news.sina.com.cn']

    def process_item(self, item, spider):
        data = dict(item)
        self.collection.insert(data)

        return item

    def close_spider(self, spider):
        self.client.close()
