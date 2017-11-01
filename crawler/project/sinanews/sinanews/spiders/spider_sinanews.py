# -*- coding: utf-8 -*-

import scrapy
import re
import ssl
import urllib2
import math
import signal
import jieba
import jieba.analyse
from optparse import OptionParser
from docopt import docopt
from lxml import etree
from scrapy.http import Request
from sinanews.items import SinanewsItem

from kazoo.client import KazooClient
import random
from time import sleep
import json
import os

topK = 2
task_dir = '/task/sinanews/'
work_co = 0
working_set = set()
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
zk = KazooClient(hosts = hosts_list)

class SpiderSinanewsSpider(scrapy.Spider):
    name = "spider_sinanews"
    allowed_domains = ["sina.com.cn"]
    start_urls = ['http://news.sina.com.cn/']

    def parse(self, response):
        home = response.xpath('//*[@id="blk_cNav2_01"]/div/a[1]/@href').extract()
        yield Request(url=home[0],callback=self.scroll)

    def scroll(self, response):

        zk.start()
        zode_path =  zk.create("/pid/sinanews/node-" , ephemeral = True, sequence = True)
        myid = zode_path[-10 : ]
        mytask_dir = task_dir + "node-" + myid
        try:
            zk.create('/task/sinanews')
            Master = True
        except :
            Master = False

        if Master == True:
            zk.create(mytask_dir)
            sleep(3)
            nodes = len(zk.get_children("/pid/sinanews"))
            data = response.xpath('//*[@id="d_list"]/div/a[12]/@href').extract()
            pages = int(re.findall('page=(.*?)&',data[0])[0])*0.82
            real_nodes = zk.get_children("/task/sinanews")
            while nodes != len(real_nodes):
                real_nodes = zk.get_children("/task/sinanews")
                nodes = len(zk.get_children("/pid/sinanews"))
                sleep(0.01)

            peer_tasks = int(pages) / nodes
            i = 0
            while i < nodes:
                j = 0
                while j < peer_tasks:
                    detail_url = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=89&num=60&page=" + str(i*peer_tasks + j + 1)
                    msg = '[{"motian":"0", "url":"' + detail_url + '", "level":"2", "content":"0"}]'
                    zk.create("/task/sinanews/" + real_nodes[i] + "/task-", value = msg, sequence = True)
                    j += 1
                i += 1
        else:
            zk.create(mytask_dir)

        while True:
            global work_co

            try:
                tasks = zk.get_children(mytask_dir)
            except Exception,e:
                print "get_children %s" % e 
            while len(tasks) == 0:
                sleep(1)
                tasks = zk.get_children(mytask_dir)
            obj_tasks = mytask_dir + '/' + tasks[random.randint(0, len(tasks) - 1)]
            working_set.add(obj_tasks)
            
            mytask_data, mytask_stat = zk.get(obj_tasks)
            
            task = json.loads(mytask_data)
            if task[0]['level'] == '2':
                url = task[0]['url']
                yield Request(url= url,meta={"task":obj_tasks,"task_dir":mytask_dir}, callback=self.news)
                work_co += 4





    def news(self, response):
        global work_co
        data = response.body.decode('GBK','ignore')
        titles = re.findall('{title : "(.*?)",id', data)
        urls = re.findall('},title : ".*?url : "(.*?)",type', data)
        length = len(titles)
        j = 0
        for i in range(length):

            # print "create success"
            # if j%3 == 0:
            #     msg = '[{"motian":"0", "url":"' + str(urls[i]) + '", "level":"3", "content":"0"}]'
            #     try:
            #         my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg, sequence = True)
            #     except Exception,e:
            #         print "create: %s"% e                
            # else:
            yield Request(url=urls[i],meta = {"item":titles[i]}, callback=self.detail)
            #j += 1
            work_co += 8
        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])
        work_co -=4

    def detail(self, response):
        print "detail"
        item = SinanewsItem()
        item['title'] = response.xpath('//div[@class="page-header"]/h1/text()').extract()[0].encode('utf-8')
        item['url'] = response.url
        item['sort'] = response.meta["item"].encode('utf-8')
        item['readnum'] = ' '
        item['releaseTime'] = response.xpath('//span[@class="time-source"]/text()').extract()[0].strip().encode('utf-8')
        tempdata = response.xpath('//div[@class="article-keywords"]/a/text()').extract()
        item['tags'] = '   '.join(tempdata).encode('utf-8')
        data = response.xpath('//div[@id="artibody"]')
        item['article'] = data.xpath('string(.)').extract()[0]
        tags = jieba.analyse.extract_tags(item['article'],topK=topK)
        item['keywords'] = (','.join(tags))
        
        print item['title']    
        #print item['releaseTime']
        #print item['tags']
        #print item['sort']

        #print item['article']
        
        yield item

        global work_co
        work_co -=8
