#!/usr/bin/env python
# coding=utf-8

import re
import urllib2
import jieba
import jieba.analyse
from time import sleep
from pymongo import MongoClient

from lxml import etree
from selenium import webdriver

topK = 2

class Crawler:
    def __init__(self, url=None):
        self.client = MongoClient('localhost', 27017)
        mdb = self.client['test']
        self.collection = mdb['test']

        self.url = url
        self.data = self.url.split('/')
        
        headers = {
                'Accept':'application/json, text/plain, */*',
                'Accept-Language':'zh-CN,zh;q=0.3',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Connection':'keep-alive',
        }

        try:
            request = urllib2.Request(url=url, headers=headers)
            response = urllib2.urlopen(request).read()
            self.tree = etree.HTML(response)
        except Exception, e:
            return '链接输入有误!!!'

    def spider_taobao(self):
        item = []
        
        try:
            if self.data[3].startswith('?spm=a21bo.50862.201857'):
                return '1级'
            elif self.data[3] == 'markets':
                return '2级'
            elif self.data[3].startswith('list'):
                driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--load-images=false'])
                driver.get(self.url)
                sleep(1)
                data = driver.page_source
                tree = etree.HTML(data)
                title = tree.xpath('//div[@class="row row-2 title"]/a/text()')
                url = 'https:' + tree.xpath('//div[@class="row row-2 title"]/a/@href')
                price = tree.xpath('//div[@class="price g_price g_price-highlight"]/strong/text()')
                shop = tree.xpath('//div[@class="shop"]/a/span[2]/text()')
                shop_url = tree.xpath('//div[@class="shop"]/a/@href')

                print title
                print url
                print price
                print shop
                print shop_url

            elif self.data[3].startswith('item'):
                print '4级'
                title = self.tree.xpath('//h3[@class="tb-main-title"]/@data-title')[0]
                url = self.url
                price = self.tree.xpath('//em[@class="tb-rmb-num"]/text()')[0]
                shop = self.tree.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/text()')[0].strip()
                shop_url = "http:" + self.tree.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/@href')[0]
                try:
                    describeScore = self.tree.xpath('//div[@class="tb-shop-rate"]/dl[1]/dd/a/text()')[0].strip()
                    serviceScore = self.tree.xpath('//div[@class="tb-shop-rate"]/dl[2]/dd/a/text()')[0].strip()
                    logisticsScore = self.tree.xpath('//div[@class="tb-shop-rate"]/dl[3]/dd/a/text()')[0].strip()
                except Exception, e:
                    describeScore = ''
                    serviceScore = ''
                    logisticsScore = ''
                thisid = re.findall('id=(.*?)$', self.url)
                commenturl = "https://rate.tmall.com/list_detail_rate.htm?itemId={}&sellerId=880734502&currentPage=1".format(thisid)
                commentdata = urllib2.urlopen(commenturl).read().decode("GBK", "ignore")
                tempdata = re.findall('("commentTime":.*?),"days"', commentdata)
                if len(tempdata) == 0:
                    tempdata = re.findall('("rateContent":.*?),"reply"', commentdata)
                comment = ""
                for data in tempdata:
                    comment += data
                
                item.append('hp')
                item.append(str(url))
                item.append(title)
                item.append(price)
                item.append(shop)
                item.append(shop_url)
                item.append(str((float(describeScore)+float(serviceScore)+float(logisticsScore))/3)[:3])
                
                return item
            elif self.data[3].startswith('?spm=a21bo.50862.201867-main'):
                return '特殊级别!'
            else:
                return '敬请期待!!!'
        except Exception, e:
            print e
            if self.data[2].endswith('taobao.com'):
                return '1级'
            else:
                return '未知错误!!!'
    
    def spider_sinablog(self):
        try:
            if self.data[3] == 's':
                title = self.tree.xpath('//*[@class="articalTitle"]/h2/text()')
                print title
                if not title:
                    title = self.tree.xpath('//div[@class="BNE_title"]/h1/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@id="pub_time"]/text()')[0]
                    allnums = self.tree.xpath('//div[@class="BNE_txtA OL"]/span/text()')
                    readnum = allnums[0][:1:-1]
                    commentnum = allnums[1][1:-1]
                    collnum = allnums[2][1:-1]
                    reprintnum = allnums[3][1:-1]

                    tempdata = self.tree.xpath('//div[@class="tagbox"]/a/text()')
                    btags = "   ".join(tempdata).encode('utf-8')
                    print title
                    print release_time
                    print readnum
                    print tempdata
                else:
                    pass
                article = ""
                data = self.tree.xpath('//*[@id="sina_keyword_ad_area2"]')
                for part in data:
                    article = part.xpath('string(.)')

                #tags = jieba.analyse.extract_tags(article,topK=topK)
                #keywords = (','.join(tags))
                
                item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n标签:  " + btags + "\n\n阅读人数:  " + readnum + "\n\n评论数:  " + commentnum + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
            #print item 
            return item
        except Exception, e:
            print e
            return '未知错误!!!'
    
    def spider_csdnblog(self):
        try:
            if self.data[5] == 'details':
                title = self.tree.xpath('//span[@class="link_title"]/a/text()')
                if not title:
                    title = self.tree.xpath('//h1[@class="csdn_top"]/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time"]/text()')[0].encode('utf-8')
                    readnum = self.tree.xpath('//button[@class="btn-noborder"]/span/text()')[0].encode('utf-8')
                    commentnum = self.tree.xpath('//button[@class="btn-noborder but-comment-topicon"]/span[1]/text()')[0].encode('utf-8')
                    tempdata = self.tree.xpath('//ul[@class="article_tags clearfix tracking-ad"]/li/a/text()')
                    btags = '   '.join(tempdata).encode('utf-8')
                    sort = self.tree.xpath('//div[@class="artical_tag"]/span[1]/text()')[0].encode('utf-8')
                else:
                    title = title[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="link_postdate"]/text()')[0]
                    readnum = self.tree.xpath('//span[@class="link_view"]/text()')[0].encode('utf-8')[:-9]
                    commentnum = self.tree.xpath('//span[@class="link_comments"]/text()')[1][1:-1]
                    tempdata = self.tree.xpath('//span[@class="link_categories"]/a/text()')
                    btags = '   '.join(tempdata).encode('utf-8')
                    print type(btags)
                    sort = ""
                    #sort = self.tree.xpath('//div[@class="category_r"]/label/span/text()')[0].encode('utf-8')
                article = ""
                data = self.tree.xpath('//*[@class="markdown_views"]')
                for part in data:
                    article += part.xpath('string(.)').encode('utf-8')
                article = article.lstrip('\r\n')
                item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n类别:  " + sort + "\n\n标签:  " + btags + "\n\n阅读人数:  " + readnum + "\n\n评论数:  " + commentnum + "\n\n收藏数:  " + collnum + "转载数: " +  + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
            return item 
        except Exception, e:
            print e
            return '未知错误!!!'
