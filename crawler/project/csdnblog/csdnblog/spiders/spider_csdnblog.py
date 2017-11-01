# -*- coding: utf-8 -*-

import scrapy
import re
import ssl
import urllib2
import lxml.html
import math
import jieba
import jieba.analyse
from optparse import OptionParser
from docopt import docopt
from scrapy.http import Request
from csdnblog.items import CsdnblogItem
from kazoo.client import KazooClient
from time import sleep
import json
import threading
import random
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


topK = 2
task_dir = '/task/csdnblog/'
work_co = 0
working_set = set()
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
zk = KazooClient(hosts = hosts_list)

class SpiderCsdnblogSpider(scrapy.Spider):
    name = "spider_csdnblog"
    allowed_domains = ["csdn.net"]
    start_urls = ['http://blog.csdn.net/peoplelist.html?channelid=0&page=1']

    def parse(self, response):
        global working_set 
        global work_co
        zk.start()
        zode_path =  zk.create("/pid/csdnblog/node-" , ephemeral = True, sequence = True)
        myid = zode_path[-10 : ]
        mytask_dir = task_dir + "node-" + myid
        try:
            zk.create('/task/csdnblog')
            Master = True
        except :
            Master = False

        if Master == True:
            zk.create(mytask_dir)
            sleep(3)
            nodes = len(zk.get_children("/pid/csdnblog"))

            data = response.xpath('/html/body/div/span/text()').extract()[0]
            pages = re.findall('共(.*?)页', str(data))[0]
            real_nodes = zk.get_children("/task/csdnblog")
            while nodes != len(real_nodes):
                real_nodes = zk.get_children("/task/csdnblog")
                nodes = len(zk.get_children("/pid/csdnblog"))
                sleep(0.01)

	  
            peer_tasks = int(pages) / nodes #tot do: chu bu jun yun ru he cao zuo ??

            i = 0
            while i < nodes:
                j = 0
                while j < peer_tasks:
                    try:
                        obj_url = 'http://blog.csdn.net/peoplelist.html?channelid=0&page='
                        msg = '[{"motian":"0", "url":"' + obj_url +str(i*peer_tasks + j + 1) + '", "level":"2", "content":"0"}]'
                        zk.create("/task/csdnblog/" + real_nodes[i] + "/task-", value = msg, sequence = True)
                    except Exception,e:
                        print "%s" % e
                    j += 1
                i += 1
        else:
            zk.create(mytask_dir)

        while True:
            global work_co
            #if work_co > 70:
            #    sleep(10)
            try:
                tasks = zk.get_children(mytask_dir)
            except Exception,e:
                print "get_children %s" % e 
            while len(tasks) == 0:
                sleep(1)
                tasks = zk.get_children(mytask_dir)
            obj_tasks = mytask_dir + '/' + tasks[random.randint(0, len(tasks) - 1)]

            mytask_data, mytask_stat = zk.get(obj_tasks)
            
      
            working_set.add(obj_tasks)
            task = json.loads(mytask_data)


            if task[0]['level'] == '2':
                temp = task[0]['url']
                work_co += 1
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.blogger)


            if task[0]['level'] == '3':
                temp = task[0]['url']
                work_co += 2
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.total)

            if task[0]['level'] == '4':
                temp = task[0]['url']
                work_co += 4
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.article)
 
            # if task[0]['level'] == '5':
            #     temp = task[0]['url']
            #     work_co += 8
            #     yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.detail)



    def blogger(self, response):
        global work_co
        global working_set
        bloggers = response.xpath('/html/body/dl/dd/a/@href').extract()
        j = 0
        for blogger in bloggers:
            
            if j%3 == 0:
                msg = '[{"motian":"0", "url":"' + blogger + '", "level":"3", "content":"0", "from":"'+ str(os.getpid())+ '"}]'
                my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg.encode("utf-8"), sequence = True)                
            else:
                try:
                    yield Request(url=blogger, meta = {"task":my_node,"task_dir":response.meta["task_dir"]},callback=self.total)
                except Exception,e:
                    print "yield %s" % e
            j += 1
        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])
        global work_co
        work_co -= 1

    def total(self, response):
        global work_co
        global working_set
        data = response.xpath('//*[@id="papelist"]/span/text()').extract()[0]
        pages = re.findall('共(.*?)页',str(data))
        j = 0
        for i in range(0,int(pages[0])):
            url = str(response.url) + '/article/list/' + str(i+1)
            
            if j%3 == 0:
                msg = '[{"motian":"0", "url":"' + url + '", "level":"4", "content":"0", "from":"'+ str(os.getpid())+ '"}]'
                my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg.encode("utf-8"), sequence = True)
            else:
                try:
                    yield Request(url= url,meta = {"task":my_node,"task_dir":response.meta["task_dir"]}, callback=self.article)
                except Exception,e:
                    print "yield %s" % e
            j += 1

        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])
        global work_co
        work_co -= 2

    def article(self, response):
        global work_co
        global working_set 
        articles = response.xpath('//span[@class="link_title"]/a/@href').extract()
        for article in articles:
            url = "http://blog.csdn.net" + article 
            try:
                yield Request(url= url, callback=self.detail)
            except Exception,e:
                print "yield %s" % e
        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])
        work_co -= 4

    def detail(self, response):
        print "detail"
        item = CsdnblogItem()

        item['url'] = response.url
        title = response.xpath('//span[@class="link_title"]/a/text()').extract()
        if not title:
            item['title'] = response.xpath('//h1[@class="csdn_top"]/text()').extract()[0].encode('utf-8')
            item['releaseTime'] = response.xpath('//span[@class="time"]/text()').extract()[0].encode('utf-8')
            item['readnum'] = response.xpath('//button[@class="btn-noborder"]/span/text()').extract()
            tempdata = response.xpath('//ul[@class="article_tags clearfix tracking-ad"]/li/a/text()').extract()
            item['tags'] = '   '.join(tempdata).encode('utf-8')
            item['sort'] = response.xpath('//div[@class="artical_tag"]/span[1]/text()').extract()[0].encode('utf-8')
        else:
            head = ""
            for t in title:
                head += t
            item['title'] = head.encode('utf-8').strip('\r\n')
            item['releaseTime'] = response.xpath('//span[@class="link_postdate"]/text()').extract()[0]
            item['readnum'] = response.xpath('//span[@class="link_view"]/text()').extract()[0].encode('utf-8')[:-9]
            tempdata = response.xpath('//span[@class="link_categories"]/a/text()').extract()
            item['tags'] = '   '.join(tempdata).encode('utf-8')
            tdata = response.xpath('//div[@class="bog_copyright"]/text()').extract()
            if not tdata:
                item['sort'] = "转载"
            else:
                item['sort'] = "原创"
            #item['sort'] = response.xpath('//div[@class="category_r"]/label/span/text()').extract()[0].encode('utf-8')
        data = response.xpath('//div[@id="article_content"]|//div[@class="markdown_views"]')
        item['article'] = data.xpath('string(.)').extract()[0]

        tags = jieba.analyse.extract_tags(item['article'],topK=topK)
        item['keywords'] = (','.join(tags))

        #print item['url']
        #print item['title']
        #print item['sort']
        #print item['keywords']
        #print item['article']

        yield item
        global work_co
        work_co -= 8

