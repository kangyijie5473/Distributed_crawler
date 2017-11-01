# -*- coding: utf-8 -*-

import scrapy
import re
import urllib2
import random
from time import sleep
from scrapy import Request
from accurate_taobao.items import AccurateTaobaoItem
from kazoo.client import KazooClient
from time import sleep
import json
import threading
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

task_dir2 = '/task/taobao'
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
work_co = 0
working_set = set()
zk = KazooClient(hosts = hosts_list)

class SpiderAccuratetaobaoSpider(scrapy.Spider):
    name = 'spider_accurate_taobao'
    allowed_domains = ['taobao.com']
    start_urls = ['https://www.taobao.com/']
    
    def __init__(self, keywords=None, *args, **kwargs):
        super(SpiderAccuratetaobaoSpider, self).__init__(*args, **kwargs)
        self.keywords = keywords
        self.start_urls = ['https://s.taobao.com/search?q=%s' % keywords]

    def parse(self, response):
        task_keyword_dir = 'taobao_' + self.keywords
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
             
            peer_tasks = 100 / nodes # pages = 50
            print "master is " + str(os.getpid())
            i = 0
            while i < nodes:
                j = 0
                while j < peer_tasks:
                    purl = response.url + "&s={}".format(str((i*peer_tasks + j)*44))
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

            working_set.add(obj_tasks)
            mytask_data, mytask_stat = zk.get(obj_tasks)
            
            task = json.loads(mytask_data)

            if task[0]['level'] == '2':
                temp = task[0]['url']
                work_co += 2
                print "get"
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.goods)





    def goods(self, response):
        print  "goods"
        global work_co
        global working_set
        body = response.body.decode("utf-8","ignore")

        patid = '"nid":"(.*?)"'
        allid = re.compile(patid).findall(body)
        for j in range(len(allid)):
            thisid = allid[j]
            url = "https://item.taobao.com/item.htm?id=" + str(thisid)
            work_co += 8
            yield Request(url=url,callback=self.next)
        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])
    def next(self, response):
        print "next"
        item = AccurateTaobaoItem()
    
        item['keywords'] = self.keywords
        item["title"] = response.xpath('//h3[@class="tb-main-title"]/@data-title').extract()[0].encode('utf-8')
        item["link"] = response.url
        item["price"] = response.xpath('//em[@class="tb-rmb-num"]/text()').extract()[0]
        item['shop'] = response.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/text()|//a[@class="shop-name-link"]/text()').extract()[0].encode('utf-8').strip()
        shop_url = 'http:' + response.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/@href|//a[@class="shop-name-link/@href"]').extract()[0]
        item['shopLink'] = shop_url
        item['describeScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[1]/dd/a/text()').extract()[0].strip()
        item['serviceScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[2]/dd/a/text()').extract()[0].strip()
        item['logisticsScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[3]/dd/a/text()').extract()[0].strip()

        #thisid = re.findall('id=(.*?)$', response.url)[0]
        #commenturl = "https://rate.tmall.com/list_detail_rate.htm?itemId={}&sellerId=880734502&currentPage=1".format(thisid)
        #commentdata = urllib2.urlopen(commenturl).read().decode("GBK", "ignore")
        #tempdata = re.findall('("commentTime":.*?),"days"', commentdata)
        #if len(tempdata) == 0:
        #    tempdata = re.findall('("rateContent":.*?),"reply"', commentdata)
        #item['commentdata'] = ""
        #for data in tempdata:
        #    item['commentdata'] += data.encode('utf-8')
        
        print item['title']
        print item['link']
        print item['price']

        yield item
        global work_co
        work_co -= 8
