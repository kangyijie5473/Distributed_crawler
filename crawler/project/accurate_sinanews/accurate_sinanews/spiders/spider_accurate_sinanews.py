    # -*- coding: utf-8 -*-

import scrapy
import re
import urllib2
import random
import jieba
import jieba.analyse
from optparse import OptionParser
from docopt import docopt
from time import sleep
from scrapy import Request
from accurate_sinanews.items import AccurateSinanewsItem
from kazoo.client import KazooClient
from time import sleep
import json
import threading
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

task_dir2 = '/task/sinanews'
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
work_co = 0
#working_set = set()
zk = KazooClient(hosts = hosts_list)

topK = 2

class SpiderAccurateSinanewsSpider(scrapy.Spider):
    name = 'spider_accurate_sinanews'
    allowed_domains = ['sina.com.cn']
    start_urls = ['https://news.sina.com.cn/']
    
    def __init__(self, keywords=None, *args, **kwargs):
        super(SpiderAccurateSinanewsSpider, self).__init__(*args, **kwargs)
        print keywords
        self.keywords = keywords
        self.start_urls = ['http://search.sina.com.cn/?q={}&range=title&c=news&sort=time&ie=utf-8'.format(keywords)]

    def parse(self, response):
        #pdata = response.xpath('//div[@class="l_v2"]/text()').extract()[0].encode('utf-8')
        #pages = int(int(re.findall('闻(.*?)篇', pdata)[0].replace(',','')) / 20)
        pages = 200
        task_keyword_dir = 'sinanews_' + self.keywords
        print task_keyword_dir 
        task_dir = task_dir2 + '_' + self.keywords + '/'
        print 'alive'

        zk.start()

        test = "/pid/" + task_keyword_dir
        try:
            zk.create(test.decode("utf-8"))
        except Exception,e:
            pass

        zode_path =  zk.create("/pid/" + task_keyword_dir + "/node-" , ephemeral = True, sequence = True)
        
        myid = zode_path[-10 : ]
        mytask_dir = task_dir + "node-" + myid
        try:
            zk.create('/task/'+ task_keyword_dir)
            Master = True
        except :
            Master = False

        if Master == True:
            zk.create(mytask_dir)
            sleep(3)
            nodes = len(zk.get_children("/pid/" +task_keyword_dir))
            real_nodes = zk.get_children("/task/" + task_keyword_dir)
            print "realnodes" + str(real_nodes)
            while nodes != len(real_nodes):
                real_nodes = zk.get_children("/task/" + task_keyword_dir)
                nodes = len(zk.get_children("/pid/" +task_keyword_dir))
                sleep(0.01)
             
            peer_tasks = pages / nodes # pages = 50
            print "master is " + str(os.getpid())
            i = 0
            while i < nodes:
                j = 0
                while j < peer_tasks:
                    purl = response.url + "&page=" + str((i*peer_tasks + j)+1)
                    msg = '[{ "url":"' + purl + '", "level":"2", "content":"0"}]'
                    zk.create(task_dir + real_nodes[i] + "/task-", value = msg, sequence = True)
                    j += 1
                i += 1
        else:
            zk.create(mytask_dir)

        print "sleep"

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

            #working_set.add(obj_tasks)
            mytask_data, mytask_stat = zk.get(obj_tasks)
            
            task = json.loads(mytask_data)

            if task[0]['level'] == '2':
                temp = task[0]['url']
                work_co += 2
                print "get"
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.article)





    def article(self, response):
        articles = response.xpath('//div[@class="r-info r-info2"]/h2/a/@href').extract()
        for url in articles:
            yield Request(url=url, callback=self.detail)
        if response.meta != None:
            zk.delete(response.meta["task"])
    def detail(self, response):
        item = AccurateSinanewsItem()
        item['keywords'] = self.keywords
        item['title'] = response.xpath('//div[@class="page-header"]/h1/text()|//h1[@id="main_title"]/text()').extract()[0].encode('utf-8')
        item['url'] = response.url
        item['sort'] = ''
        item['readnum'] = ''
        item['releaseTime'] = response.xpath('//span[@class="time-source"]/text()').extract()[0].strip().encode('utf-8')
        tempdata = response.xpath('//div[@class="article-keywords"]/a/text()').extract()
        item['tags'] = '   '.join(tempdata).encode('utf-8')
        data = response.xpath('//*[@id="artibody"]')
        item['article'] = data.xpath('string(.)').extract()[0]
        #tags = jieba.analyse.extract_tags(item['article'],topK=topK)
        #item['keywords'] = (','.join(tags))

        print item['title']
        #print item['url']
        #print item['releaseTime']
        #print item['tags']
        #print item['keywords']

        yield item

