#!/usr/bin/env python
# coding=utf-8

import re
from crawler import Crawler
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

url = raw_input('请输入url: ')

if not url.startswith('http'):
    url = 'http://' + url
if url.endswith('com') or url.endswith('net'):
    url = url + '/'

print '修正后链接: ', url
crawl = Crawler(url)
a = []

if re.search('taobao|jiyoujia', url):
    a.append(str(crawl.spider_taobao()))
elif re.search('tmall', url):
    a.append(str(crawl.spider_tmall()))
elif re.search('jd.com', url):
    a.append(str(crawl.spider_jingdong()))
elif re.search('blog.sina', url):
    a.append(str(crawl.spider_sinablog()))
elif re.search('csdn', url):
    a.append(str(crawl.spider_csdnblog()))
elif re.search('sina.com.cn', url):
    a.append(str(crawl.spider_sinanews()))


print a

