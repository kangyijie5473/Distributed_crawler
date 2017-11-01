# -*- coding: utf-8 -*-

import os
import scrapy
import socket
import json
import re
import urllib2
import threading
import random
from time import sleep
from scrapy.http import Request
from taobao.items import TaobaoItem
from kazoo.client import KazooClient
#import logging

task_dir = '/task/taobao/'
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
work_co = 0
working_set = set()
zk = KazooClient(hosts = hosts_list)
#logging.basicConfig()


class SpiderTaobaoSpider(scrapy.Spider):
    
    name = "spider_taobao"
    allowed_domains = ["taobao.com"]
    start_urls = ['https://www.taobao.com/']

    def parse(self, response):

        zk.start()
        zode_path =  zk.create("/pid/taobao/node-" , ephemeral = True, sequence = True)
        myid = zode_path[-10 : ]
        mytask_dir = task_dir + "node-" + myid
        try:
            zk.create('/task/taobao')
            Master = True
        except :
            Master = False

        if Master == True:
            zk.create(mytask_dir)
            sleep(3)
            themes = response.xpath('//ul[@class="service-bd"]/li/span/a/@href').extract()
            nodes = len(zk.get_children("/pid/taobao"))
            real_nodes = zk.get_children("/task/taobao")
            print "realnodes" + str(real_nodes)
            while nodes != len(real_nodes):
                real_nodes = zk.get_children("/task/taobao")
                nodes = len(zk.get_children("/pid/taobao"))
                sleep(0.01)
             
            peer_tasks = len(themes) / nodes
            print "master is " + str(os.getpid())
            i = 0
            while i < nodes:
                j = 0
                while j < peer_tasks:
                    msg = '[{ "url":"' + str(themes[i*peer_tasks+j]) + '", "level":"2", "content":"0"}]'
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
                temp = task[0]['url'].split(':')
                work_co += 1
                yield Request(url='http:' + temp[len(temp)-1],meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.classification)

            if task[0]['level'] == '3':
                temp = task[0]['url']
                work_co += 2
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.pageturning)

            if task[0]['level'] == '4':
                temp = task[0]['url']
                work_co += 4
                yield Request(url=temp,meta={"task":obj_tasks,"task_dir":mytask_dir},callback=self.goods)
 



    def classification(self, response):
        global work_co
        global working_set
        i = 0
        sorts = response.xpath('//dl[@class="theme-bd-level2"]/dd/a/@href').extract()

        if len(sorts) == 0:
            msg = '[{"motian":"0", "url":"' + response.url + '", "level":"3", "content":"0", "from":"'+ str(os.getpid())+ '"}]'
            my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg.encode("utf-8"), sequence = True)
            yield Request(url=response.url,meta = {"task":my_node,"task_dir":response.meta["task_dir"]},callback=self.pageturning)
        else:
            for sort in sorts:
                temp = sort.split(':')
                url = 'http:' + temp[len(temp) - 1]
                msg = '[{"motian":"0", "url":"' + url + '", "level":"3", "content":"0", "from":"'+ str(os.getpid())+ '"}]'
                if i%3 == 0:
                    my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg.encode("utf-8"), sequence = True)
                else:
                    try:
                        work_co += 2
                        yield Request(url= url, callback=self.pageturning)
                    except Exception,e:
                        print "yield %s" % e
                i += 1
            if response.meta != None:
                zk.delete(response.meta["task"])
                working_set.remove(response.meta["task"])
            work_co -=1

    def pageturning(self, response):
        global work_co
        global working_set
        j = 0
        for i in range(10):
            purl = response.url + "&bcoffset=12&s={}".format(str(i*60))
            if j%3 == 0:
                msg = '[{"motian":"0", "url":"' + purl + '", "level":"4", "content":"0"}]'
                my_node=zk.create(response.meta["task_dir"] + "/task-", value = msg, sequence = True)
            else:
                work_co += 4
                yield Request(url=purl, callback=self.goods)
            j += 1
        if response.meta != None:
            zk.delete(response.meta["task"])
            working_set.remove(response.meta["task"])

        work_co -= 2

    def goods(self, response):
        global work_co
        i = 0
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

        work_co -= 4

    def next(self, response):
        item = TaobaoItem()

        item["title"] = response.xpath('//h3[@class="tb-main-title"]/@data-title').extract()[0].encode('utf-8')
        item["link"] = response.url
        item["price"] = response.xpath('//em[@class="tb-rmb-num"]/text()').extract()[0]
        item['shop'] = response.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/text()').extract()[0].encode('utf-8').strip()
        shop_url = 'http:' + response.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/@href').extract()[0]
        item['shopLink'] = shop_url
        try:
            item['describeScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[1]/dd/a/text()').extract()[0].strip()
            item['serviceScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[2]/dd/a/text()').extract()[0].strip()
            item['logisticsScore'] = response.xpath('//div[@class="tb-shop-rate"]/dl[3]/dd/a/text()').extract()[0].strip()
        except Exception, e:
            item['describeScore'] = ""
            item['serviceScore'] = ""
            item['logisticsScore'] = ""
        print item["title"]
        yield item
        global work_co
        work_co -= 8
