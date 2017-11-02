#!/usr/bin/env python
# coding=utf-8

import re
import urllib2
import threading
import json
import jieba
from time import sleep
from lxml import etree
from chardet import detect
from selenium import webdriver
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

topK = 2

taobao_goods = []
tmall_goods = []
jingdong_goods = []

def tmall_list(url, price, headers):
    try:
        request = urllib2.Request(url=url, headers=headers)
        res = urllib2.urlopen(request).read()
        tree = etree.HTML(res)
    except Exception, e:
        return "链接错误"
        print 'Error: %s' % e
    try:
        title = tree.xpath('//div[@class="tb-detail-hd"]/h1/text()')[0].encode('utf-8').strip()
        shop = tree.xpath('//a[@class="slogo-shopname"]/strong/text()')[0].encode('utf-8').strip()
        shop_url = 'https:' + tree.xpath('//a[@class="slogo-shopname"]/@href')[0]
        describeScore = tree.xpath('//div[@id="shop-info"]/div[2]/div[1]/div[2]/span/text()')[0]
        serviceScore = tree.xpath('//div[@id="shop-info"]/div[2]/div[2]/div[2]/span/text()')[0]
        logisticsScore = tree.xpath('//div[@id="shop-info"]/div[2]/div[3]/div[2]/span/text()')[0]
        
        tmall_goods.append(url)
        tmall_goods.append(unicode(title))
        tmall_goods.append(price)
        tmall_goods.append(unicode(shop))
        tmall_goods.append(shop_url)
        tmall_goods.append(str((float(describeScore)+float(serviceScore)+float(logisticsScore))/3)[:3])
    except Exception, e:
        pass

def jingdong_list(url):
    try:
        res = urllib2.urlopen(url).read().decode('GBK', 'ignore')
        tree = etree.HTML(res)
    except Exception, e:
        print "Error: %s" % e
    title = tree.xpath('//div[@class="sku-name"]/text()')[0].encode('utf-8').strip()
    shop = tree.xpath('//div[@class="name"]/a/text()')[0].encode('utf-8').strip()
    shop_url = 'https:' + tree.xpath('//div[@class="name"]/a/@href')[0]
    try:
        compositeScore = tree.xpath('//em[@class="evaluate-grade"]/span/a/text()')[0]
    except Exception, e:
        compositeScore = ''

    data = url.split('/')
    skuids = data[3][:-5]
    purl = 'https://p.3.cn/prices/mgets?skuIds=J_' + skuids
    pricedata = urllib2.urlopen(purl).read()
    jdata = json.loads(pricedata)
    price = jdata[0]["p"]

    jingdong_goods.append(url)
    jingdong_goods.append(unicode(title))
    jingdong_goods.append(price)
    jingdong_goods.append(unicode(shop))
    jingdong_goods.append(shop_url)
    jingdong_goods.append(compositeScore)

def taobao_list(thisid, headers):
    gurl = "https://item.taobao.com/item.htm?id=" + str(thisid)
    try:
        request = urllib2.Request(url=gurl, headers=headers)
        res = urllib2.urlopen(request).read().decode('gb2312', 'ignore')
        tree = etree.HTML(res)
    except Exception, e:
        print 'taobao detailPage open failed: %s' % e
    try:
        title = tree.xpath('//h3[@class="tb-main-title"]/text()|//div[@class="tb-detail-hd"]/h1/a/text()')[0].strip().strip('\r\n').encode('utf-8')
    except Exception, e:
        print gurl
        title = tree.xpath('//div[@class="tb-detail-hd"]/h1/text()')[0].strip()
        print title
    #price = tree.xpath('//em[@class="tb-rmb-num"]/text()')[0]
    url = "https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={}&modules=price,xmpPromotion".format(thisid)
    req = urllib2.Request(url=url, headers=headers)
    res = urllib2.urlopen(req).read()
    data = list(set(re.findall('"price":"(.*?)"', res)))
    price = ""
    for t in data:
        if '-' in t:
            price = t
            break
    if not price:
        price = sorted(map(float, data))[0]
    #print price
    try:
        shop = tree.xpath('//div[@id="J_ShopInfo"]//dl/dd/strong/a/text()|//a[@class="shop-name-link"]/text()')[0].strip()
        shop_url = "http:" + tree.xpath('//*[@id="J_ShopInfo"]//dl/dd/strong/a/@href|//a[@class="shop-name-link"]/@href')[0]
    except Exception, e:
        print '店铺: ', gurl
        shop = u"淘宝店铺"
        shop_url = u"https://www.taobao.com/"
    try:
        describeScore = tree.xpath('//div[@class="tb-shop-rate"]/dl[1]/dd/a/text()')[0].strip()
        serviceScore = tree.xpath('//div[@class="tb-shop-rate"]/dl[2]/dd/a/text()')[0].strip()
        logisticsScore = tree.xpath('//div[@class="tb-shop-rate"]/dl[3]/dd/a/text()')[0].strip()
    except Exception, e:
        describeScore = '0'
        serviceScore = '0'
        logisticsScore = '0'

    taobao_goods.append(gurl)
    taobao_goods.append(unicode(title))
    taobao_goods.append(price)
    taobao_goods.append(shop)
    taobao_goods.append(shop_url)
    taobao_goods.append(str((float(describeScore)+float(serviceScore)+float(logisticsScore))/3)[:3])

class Crawler:
    def __init__(self, url=None):
        self.client = MongoClient('localhost', 27017)
        mdb = self.client['test']
        self.collection = mdb['test']

        self.url = url
        self.data = self.url.split('/')
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'referer': 'https://item.taobao.com/item.htm?id=543224175019',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Connection': 'keep-alive',
            'cookie': 'thw=cn; miid=1877326715353705246; ctoken=0P0JvKEIyk15qEwpK8LIiceland; UM_distinctid=15e22e6bc6e1-0c5735b42741ab-3976045e-100200-15e22e6bc6f435; hng=CN%7Czh-CN%7CCNY%7C156; v=0; tk_trace=oTRxOWSBNwn9dPyscxqAz9fIO73QQFhF7kVkgTL59JVC7kpGpQEdOb67caDmPjbIYxYMRUFQxbzTrNIXyEycFIbsSXtHRwYQoI0GecDqZOBXLhu6GOl%2FUqYI1BXllibVbD3hDwIDgFtUI1BuM8jNCjYGTh97gcLVXlpo6B%2FaYHov3d8iHYgfcw0mnNRt5P60wglG6cRFjM%2F6NxolOJxHyab22uITZFuDn4ByYisAHtJROAnpqFMj9iW%2F%2Bh3XIGjvM1taR%2FScR5xO24c8oI01Nf9%2BaOXPOSRM4eoI2qYjgYRvyFpFfLaQBKiwfnUujNJXS3QPuGfhFhKe069gXSGkjTbJBhmt%2FPfWk7fE; _m_h5_tk=2f6f4667bd23f32c1dbb28fd3cf43157_1504323674917; _m_h5_tk_enc=aff23a4d091b6807fd1f9f4da94d5d4e; linezing_session=QJXBwjEeb4zxNhS670MXjI85_15043334118470iaM_13; uss=BqeJtzLVJrTsSJ6X2LDYRdaWQ%2BKUXOOY8l7NE73sSoPSShTwCqvcl%2FyDvA%3D%3D; _tb_token_=533b3393509e0; whl=-1%260%260%261504499941774; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; uc3=sg2=VypZNAKKWWqEaSKA1GpGs%2B8tysrnwEF9TzJHu9Fo6tw%3D&nk2=F5RDKmmBskqoP%2BFa&id2=UU27LTb95wEmtQ%3D%3D&vt3=F8dBzWfWVh1WNce3UbA%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D; existShop=MTUwNDU4MDM1NQ%3D%3D; lgc=tb6668866688; tracknick=tb6668866688; cookie2=1055c0500c661fa5398031aa3bd27f5c; sg=897; cookie1=B0eg4Md2wVeUEGrrbnYlnTqeCodw3QYsxMUcV2cWzeY%3D; unb=2592924029; skt=78d028e2231fda24; t=f24179ca58a99063c6f1feabcbc17b12; _cc_=V32FPkk%2Fhw%3D%3D; tg=0; _l_g_=Ug%3D%3D; _nk_=tb6668866688; cookie17=UU27LTb95wEmtQ%3D%3D; uc1=cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&cookie21=UIHiLt3xThN%2B&cookie15=W5iHLLyFOGW7aA%3D%3D&existShop=false&pas=0&cookie14=UoTcC%2Bn0xjJtlw%3D%3D&tag=8&lng=zh_CN; mt=ci=115_1&cyk=1_0; cna=jiIfEsNey0MCAXUg2C6F55ir; ucn=center; isg=AvDwL4pKXV21IQFuDiYidVT6wbeCkf8KM7tDyOpBvMsepZBPkkmkE0aVi5s-',
        }

        try:
            request = urllib2.Request(url=url, headers=self.headers)
            self.response = urllib2.urlopen(request).read()
            self.tree = etree.HTML(self.response)
        except Exception, e:
            print  "Url open failed: %s" % e
            return ["hp", unicode("链接"),unicode("有误"),unicode("请"),unicode("重新"),unicode("输入"),'!!!']

    def spider_taobao(self):
        item = []
        print self.data[2]
        print self.data[3]
        try:
            if self.data[2][2] == 'i' or self.data[2].startswith('wujin') or self.data[3].startswith('mar'):
                print 'Markets pei'
                del taobao_goods[:]
                item.append('hp')
                sids = re.findall('tce_sid&quot;:(.*?),&quot;', self.response)
                print sids
                tce_sids = ",".join(list(set(sids))).replace('}', '')
                print tce_sids
                url = 'https://tce.taobao.com/api/mget.htm?callback=jsonp235&tce_sid={}'.format(tce_sids)
                data = urllib2.urlopen(url).read().decode('GBK', 'ignore')
                itemIds = re.findall('&id=(.*?)"', data)[:60]
                print itemIds
                print len(itemIds)

                for itemId in itemIds:
                    t = threading.Thread(target=taobao_list, args=(itemId, self.headers))
                    t.start()
                
                sleep(2)
                item.extend(taobao_goods)

                return item
            
            elif self.data[2].startswith('xue'):
                print '学习'
                del taobao_goods[:]
                item.append('hp')
                url = 'https://i.xue.taobao.com/json/asynHomeDataNew.do?actionType=3&id=15'
                html_data = urllib2.urlopen(url).read().decode('GBK', 'ignore')
                tdata = re.findall('"\d.*?":(.*?]),"', html_data)
                for data in tdata:
                    #jdata = json.loads(data)
                    print data
            
            elif self.data[2].startswith('www') or self.data[3].startswith('?spm=a21bo.50862.201857'):
                print '淘宝首页'
                del taobao_goods[:]
                item.append('hp')
                url = 'https://tui.taobao.com/recommend?appid=2493&callback=jsonp1312'
                data = urllib2.urlopen(url).read().decode('GBK', 'ignore')
                itemIds = re.findall('"itemId":(.*?),"', data)
                print len(itemIds)
                for itemId in itemIds:
                    t = threading.Thread(target=taobao_list, args=(itemId, self.headers))
                    t.start()
                
                sleep(2)
                item.extend(taobao_goods)

                return item
            
            elif self.data[3].startswith('list') or self.data[3].startswith('search'):
                print '淘宝列表页'
                del taobao_goods[:]
                item.append('hp')
                patid = '"nid":"(.*?)"'
                allid = re.findall(patid, self.response)
                print allid
                for thisid in allid:
                    t = threading.Thread(target=taobao_list, args=(thisid, self.headers))
                    t.start()
                
                sleep(3)
                item.extend(taobao_goods)

                return item

            elif self.data[3].startswith('item'):
                print '淘宝详情页'
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
                
                item.append('hp')
                item.append(str(url))
                item.append(title)
                item.append(price)
                item.append(shop)
                item.append(shop_url)
                item.append(str((float(describeScore)+float(serviceScore)+float(logisticsScore))/3)[:3])
                
                return item

            #elif self.data[3].startswith('?spm=a21bo.50862.201867-main'):
            #    return ["hp", unicode("待定!!!"),'','','','','']
            else:
                return ["hp", unicode("当前"),unicode("链接"),'',unicode("暂不"),unicode("支持"),'!!!']

        except Exception, e:
            print 'Taobao error: %s' % e
            return ["hp", unicode("当前"),unicode("链接"),'',unicode("暂不"),unicode("支持"),'!!!']
    
    def spider_tmall(self):
        item = []
        print self.data[2]
        print self.data[3]
        try:
            if self.data[2].startswith('car'):
                item.append('hp')
                gurls = self.tree.xpath('//div[starts-with(@class,"col")]/a/@href')
                num = len(gurls)

                for i in xrange(num):
                    gurl = "https:" + gurls[i]
                    #print gurl
                    #itemId = re.findall('id=(.*?)&', gurl)
                    #if not itemId:
                    #    continue
                    #priceurl = "https://mdskip.taobao.com/core/initItemDetail.htm?&itemId=" + itemId[0]
                    #headers = self.headers
                    #headers['referer'] = "https://detail.tmall.com/item.htm"
                    #req = urllib2.Request(url=priceurl, headers=headers)
                    #res = urllib2.urlopen(req).read()
                    #print res
                    #sleep(1)
                    #data = re.findall('"postageFree":false,"price":"(.*?)","promType"', res)
                    #price = list(set(data))[0]

                    #print priceurl

                    t = threading.Thread(target=tmall_list, args=(gurl, "点击url查看定金", self.headers))
                    t.start()
                
                sleep(1.2)
                item.extend(tmall_goods)
                return item

            elif self.data[3].startswith('search'):
                del tmall_goods[:]
                item.append('hp')
                gurls = self.tree.xpath('//p[@class="productTitle"]/a/@href')
                prices = self.tree.xpath('//p[@class="productPrice"]/em/@title')
                
                num = len(gurls)

                for i in xrange(num):
                    gurl = "https:" + gurls[i]
                    t = threading.Thread(target=tmall_list, args=(gurl, prices[i], self.headers))
                    t.start()
                
                sleep(1.2)
                item.extend(tmall_goods)
                return item

            elif self.data[3].startswith('item'):
                print self.url
                
                headers = self.headers
                headers['referer'] = "https://detail.tmall.com/item.htm"
                itemId = re.findall('id=(.*?)&', self.url)[0]
                priceurl = "https://mdskip.taobao.com/core/initItemDetail.htm?&itemId=" + itemId
                
                req = urllib2.Request(url=priceurl, headers=headers)
                res = urllib2.urlopen(req).read()
                data = re.findall('"postageFree":false,"price":"(.*?)","promType"', res)
                price = list(set(data))[0]

                title = self.tree.xpath('//div[@class="tb-detail-hd"]/h1/text()')[0].encode('utf-8').strip()
                url = self.url
                shop = self.tree.xpath('//a[@class="slogo-shopname"]/strong/text()')[0].encode('utf-8').strip()
                shop_url = 'https:' + self.tree.xpath('//a[@class="slogo-shopname"]/@href')[0]
                describeScore = self.tree.xpath('//div[@id="shop-info"]/div[2]/div[1]/div[2]/span/text()')[0]
                serviceScore = self.tree.xpath('//div[@id="shop-info"]/div[2]/div[2]/div[2]/span/text()')[0]
                logisticsScore = self.tree.xpath('//div[@id="shop-info"]/div[2]/div[3]/div[2]/span/text()')[0]
                

                item.append('hp')
                item.append(str(url))
                item.append(unicode(title))
                item.append(price)
                item.append(unicode(shop))
                item.append(shop_url)
                item.append(str((float(describeScore)+float(serviceScore)+float(logisticsScore))/3)[:3])
                
                return item

        except Exception, e:
            return ["hp", unicode("当前"),unicode("链接"),'',unicode("暂不"),unicode("支持"),'!!!']
   
    def spider_jingdong(self):
        item = []
        print self.data
        try:
            if self.data[2].startswith('list'):
                del jingdong_goods[:]
                item.append('hp')
                urls = self.tree.xpath('//div[@id="plist"]/ul/li/div/div/div[2]/div[1]/div[3]/a/@href')
                
                for url in urls:
                    gurl = "https:" + url
                    t = threading.Thread(target=jingdong_list, args=(gurl,))
                    t.start()
            
                sleep(2)
                item.extend(jingdong_goods)

                return item

            elif self.data[2].startswith('search'):
                del jingdong_goods[:]
                item.append('hp')
                urls = self.tree.xpath('//div[@id="J_goodsList"]/ul/li/div/div/a/@href')
                
                for url in set(urls):
                    if url.startswith('//item'):
                        gurl = "https:" + url
                        print gurl
                        t = threading.Thread(target=jingdong_list, args=(gurl,))
                        t.start()
            
                sleep(2)
                item.extend(jingdong_goods)

                return item

            elif self.data[2].startswith('item'):
                print self.url
                #print self.response.decode("GBK", "ignore")

                title = self.tree.xpath('//div[@class="sku-name"]/text()')[0].encode('utf-8').strip()
                shop = self.tree.xpath('//div[@class="name"]/a/text()')[0].encode('utf-8').strip()
                shop_url = 'https:' + self.tree.xpath('//div[@class="name"]/a/@href')[0]
                try:
                    compositeScore = self.tree.xpath('//em[@class="evaluate-grade"]/span/a/text()')[0]
                except Exception, e:
                    compositeScore = ''
                
                data = self.url.split('?')[0].split('/')
                skuids = data[3][:-5]
                purl = 'https://p.3.cn/prices/mgets?skuIds=J_' + skuids
                pricedata = urllib2.urlopen(purl).read()
                jdata = json.loads(pricedata)
                price = jdata[0]["p"]

                print title
                print self.url
                print price
                print shop
                print shop_url
                print compositeScore

                item.append('hp')
                item.append(self.url)
                item.append(unicode(title))
                item.append(price)
                item.append(unicode(shop))
                item.append(shop_url)
                item.append(compositeScore)
        
                return item
        except Exception, e:
            return ["hp", unicode("当前"),unicode("链接"),'',unicode("暂不"),unicode("支持"),'!!!']

    def spider_sinablog(self):
        try:
            if self.data[3] == 's':
                title = self.tree.xpath('//*[@class="articalTitle"]/h2/text()')
                print title
                if not title:
                    title = self.tree.xpath('//div[@class="BNE_title"]/h1/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@id="pub_time"]/text()')[0]
                    tempdata = self.tree.xpath('//div[@class="tagbox"]/a/text()')
                    btags = "   ".join(tempdata).encode('utf-8')
                    print title
                    print release_time
                    print tempdata
                else:
                    title = title[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time SG_txtc"]/text()')[0]
                    tempdata = self.tree.xpath('//td[@class="blog_tag"]/h3/text()')
                    btags = "   ".join(tempdata).encode('utf-8')

                article = ""
                data = self.tree.xpath('//*[@id="sina_keyword_ad_area2"]')
                for part in data:
                    article = part.xpath('string(.)').encode('utf-8')
                article = article.lstrip('\r\n')
                #tags = jieba.analyse.extract_tags(article,topK=topK)
                #keywords = (','.join(tags))
                
                item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n标签:  " + btags + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
            
            return item
        except Exception, e:
            print e
            return '未知错误!!!'
    
    def spider_csdnblog(self):
        try:
            print self.data
            if len(self.data)==4 and self.data[3]=='' or self.data[3].endswith('html'):
                item = ""
                print 'CSDN首页'
                username = self.tree.xpath('//a[@class="nickname"]/text()')
                userlink = self.tree.xpath('//a[@class="nickname"]/@href')
                title = self.tree.xpath('//h3[@class="tracking-ad"]/a/text()')
                url = self.tree.xpath('//h3[@class="tracking-ad"]/a/@href')
                sort = self.tree.xpath('//div[@class="blog_list_b_l fl"]')
                slink = self.tree.xpath('//div[@class="blog_list_b_l fl"]')
                print slink[0].xpath('//span/a/text()')[0]
                print slink
                num = len(username)
                print  num
                print len(sort)
                for i in range(num):
                    try:
                        sortname = slink[i].xpath('//span/a/text()')[0]
                        sortlink = 'http://blog.csdn.net' + slink[i].xpath('//span/a/@href')[0]
                    except Exception, e:
                        sortname = ' '
                        sortlink = ' '

                    item += "\n用户名:  " + username[i] + "                              用户url:  " + userlink[i] + "\n文章标题:  " + title[i] + "                  文章url:  " + url[i] + "\n文章分类:  " + sortname + "                    该分类url:  " + sortlink + "\n\n\n"
                return item

            elif self.data[4] == 'newarticle.html':
                print '博文分类'
                item = "分类:  " + self.tree.xpath('//div[starts-with(@class,"category_sec_l")]/em/text()')[0].encode('utf-8') + "\n"
                username = self.tree.xpath('//a[@class="nickname"]/text()')
                userlink = self.tree.xpath('//a[@class="nickname"]/@href')
                title = self.tree.xpath('//h3[@class="tracking-ad"]/a/text()')
                url = self.tree.xpath('//h3[@class="tracking-ad"]/a/@href')

                num = len(username)
                for i in range(num):
                    item += "用户名:  " + username[i] + "        用户url:  " + userlink[i] + "\n文章标题:  " + title[i] + "        文章url:  " + url[i] + "\n\n\n"
                return item

            elif self.data[4].startswith('detail'):
                if self.data[2].startswith('geek'):
                    print '极客头条'
                    title = self.tree.xpath('//dl[@class="header  bor"]/dd/h2/span/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time"]/text()')[0].encode('utf-8')
                    readnum = self.tree.xpath('//i[@class="fa"]/b/text()')[0]
                    tempdata = self.tree.xpath('//a[@class="label label-default"]/text()')
                    btags = '   '.join(tempdata).encode('utf-8')
                    sort = self.tree.xpath('//a[@class="forum_name forum_for_cmmde"]/text()')[0].encode('utf-8')
                    article = ""
                    data = self.tree.xpath('//div[@class="description markdown_views clearfix"]')
                    for part in data:
                        article += part.xpath('string(.)').encode('utf-8')
                    article = article.lstrip('\r\n')
                    
                    print title
                    print release_time
                    print readnum
                    print btags
                    print sort
                    item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n类别:  " + sort + "\n\n标签:  " + btags + "\n\n阅读人数:  " + readnum + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
                    return item
                else:
                    print '行家'
                    return '暂不支持!!!'

            elif self.data[5] == 'details':
                print 'CSDN详情页'
                title = self.tree.xpath('//span[@class="link_title"]/a/text()')
                if not title:
                    title = self.tree.xpath('//h1[@class="csdn_top"]/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time"]/text()')[0].encode('utf-8')
                    readnum = self.tree.xpath('//button[@class="btn-noborder"]/span/text()')[0]
                    tempdata = self.tree.xpath('//ul[@class="article_tags clearfix tracking-ad"]/li/a/text()')
                    btags = '   '.join(tempdata).encode('utf-8')
                    sort = self.tree.xpath('//div[@class="artical_tag"]/span[1]/text()')[0].encode('utf-8')
                else:
                    head = ""
                    for t in title:
                        head += t
                    title = head.encode('utf-8').strip('\r\n')
                    release_time = self.tree.xpath('//span[@class="link_postdate"]/text()')[0]
                    readnum = self.tree.xpath('//span[@class="link_view"]/text()')[0].encode('utf-8')[:-9]
                    tempdata = self.tree.xpath('//span[@class="link_categories"]/a/text()')
                    btags = '   '.join(tempdata).encode('utf-8')
                    print type(btags)
                    tdata = self.tree.xpath('//div[@class="bog_copyright"]/text()')
                    if not tdata:
                        sort = "转载"
                    else:
                        sort = "原创"

                    #sort = self.tree.xpath('//div[@class="category_r"]/label/span/text()')[0].encode('utf-8')
                article = ""
                data = self.tree.xpath('//*[@class="markdown_views"]')
                if not data:
                    data = self.tree.xpath('//div[@id="article_content"]')

                for part in data:
                    article += part.xpath('string(.)').encode('utf-8')
                article = article.lstrip('\r\n')
                

                item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n类别:  " + sort + "\n\n标签:  " + btags + "\n\n阅读人数:  " + readnum + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
                return item
        
        except Exception, e:
            print 'Csdn blog error: %s' % e
            return '暂不支持!!!'

    def spider_sinanews(self):
#        try:
#            headers = self.headers
#            headers['Accept-Language'] = 'zh-CN,zh;q=0.8,en;q=0.6'
#            request = urllib2.Request(url=self.url, headers=headers)
#            response = urllib2.urlopen(request).read()
#            print response
#            print re.findall('<h1 class="article-a__title" id="j_title">(.*?)</h1>', response)[0]
#            tree = etree.HTML(response)
#        except Exception, e:
#            print  "Url open failed: %s" % e
#            return ["hp", unicode("链接"),unicode("有误"),unicode("请"),unicode("重新"),unicode("输入"),'!!!']
        
        try:
            print self.data
            if self.data[4].startswith('doc') or self.data[5].startswith('doc') or self.data[6].startswith('doc') or self.data[7].startswith('doc'):
                print '新浪新闻详情页'
                readnum = ' '
                if self.data[2].startswith('tech'):
                    sort = '科技'
                    title = self.tree.xpath('//h1[@id="main_title"]/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time-source"]/span[1]/text()')[0].encode('utf-8')
                    print title
                    print release_time
                elif self.data[2].startswith('sport'):
                    sort = '体育'
                    #title = tree.xpath('//h1[@id="j_title"]/text()')[0].encode('utf-8')
                    title = re.findall('<h1 class="article-a__title" id="j_title">(.*?)</h1>', self.response)[0]
                    #print detect(title)['encoding']
                    #release_time = tree.xpath('//span[@class="article-a__time"]/text()')[0].encode('utf-8')
                    release_time = re.findall('<span class="article-a__time">(.*?)</span>', self.response)[0]
                    tempdata = re.findall('<a href="http://tags\.sports\.sina\.com\.cn.*?target="_blank">(.*?)</a>', self.response)
                    ntags = '   '.join(tempdata).encode('utf-8')
                    print ntags
                    print title
                    print release_time
                    article = ''
                    data = self.tree.xpath('//*[@id="artibody"]')
                    for part in data:
                        article += part.xpath('string(.)').encode('utf-8')
                    article = article.lstrip('\r\n')
                    print article
                    item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n类别:  " + sort + "\n\n标签:  " + ntags + "\n\n阅读人数:  " + readnum + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
                    return item
                elif self.data[2].startswith('news'):
                    title = self.tree.xpath('//h1[@id="artibodyTitle"]/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@class="time-source"]/text()')[0].encode('utf-8')
                    sort = self.tree.xpath('//div[@class="bread"]/a/text()')[0].encode('utf-8')
                    print title
                    print release_time
                    print sort
                elif self.data[2].startswith('mil'):
                    sort = '军事'
                    title = self.tree.xpath('//h1[@id="main_title"]/text()')[0].encode('utf-8').strip()
                    release_time = self.tree.xpath('//span[@class="time-source"]/span[1]/text()')[0].encode('utf-8').strip()
                    print title
                    print release_time
                elif self.data[2].startswith('finance'):
                    sort = '财经'
                    title = self.tree.xpath('//h1[@id="artibodyTitle"]/text()')[0].encode('utf-8')
                    release_time = self.tree.xpath('//span[@id="pub_date"]/text()')[0].encode('utf-8').strip()
                    print title
                    print release_time
                elif self.data[2].startswith('ent'):
                    sort = '娱乐'
                    title = self.tree.xpath('//h1[@id="main_title"]/text()')[0].encode('utf-8').strip()
                    release_time = self.tree.xpath('//span[@class="time-source"]/span[1]/text()')[0].encode('utf-8').strip()
                    print title
                    print release_time
                
                tempdata = self.tree.xpath('//*[contains(@class,"keyword")]/a/text()')
                ntags = '   '.join(tempdata).encode('utf-8')
                print ntags
                article = ''
                data = self.tree.xpath('//*[@id="artibody"]')
                for part in data:
                    article += part.xpath('string(.)').encode('utf-8')
                article = article.lstrip('\r\n')
                print article
                item = "标题:  " + title.strip() + "\n\n发布时间:  " + release_time + "\n\n类别:  " + sort + "\n\n标签:  " + ntags + "\n\n阅读人数:  " + readnum + "\n\n正文: \n\n" + article.rstrip('\r\n') + "\n\n"
                return item

        except Exception, e:
            print 'Sina news error: %s' % e
            return "暂不支持"
    
    def spider_chinanews(self):
        pass
