#!/usr/bin/env python
# coding=utf-8


# This is a clear-all-MongoDB script 

from pymongo import MongoClient

client1 = MongoClient('47.93.198.31', 27017)
client2 = MongoClient('47.94.155.238', 27017)
client3 = MongoClient('101.200.55.43', 27017)

mdb1 = client1['479319831']
mdb2 = client2['4794155238']
mdb3 = client3['1012005543']

coll1 = mdb1['www.taobao.com']
coll2 = mdb2['www.taobao.com']
coll3 = mdb3['www.taobao.com']
coll4 = mdb1['blog.csdn.net']
coll5 = mdb2['blog.csdn.net']
coll6 = mdb3['blog.csdn.net']
coll7 = mdb1['news.sina.com.cn']
coll8 = mdb2['news.sina.com.cn']
coll9 = mdb3['news.sina.com.cn']
coll10 = mdb1['ctoblog']
coll11 = mdb2['ctoblog']
coll12 = mdb3['ctoblog']
coll13 = mdb1['www.cnblogs.com']
coll14 = mdb2['www.cnblogs.com']
coll15 = mdb3['www.cnblogs.com']


coll1.remove({})
coll2.remove({})
coll3.remove({})
coll4.remove({})
coll5.remove({})
coll6.remove({})
coll7.remove({})
coll8.remove({})
coll9.remove({})
coll10.remove({})
coll11.remove({})
coll12.remove({})
coll13.remove({})
coll14.remove({})
coll15.remove({})
