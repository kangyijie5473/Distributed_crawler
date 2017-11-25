#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import SocketServer
import re
import json
import signal
import random
import pymysql
import mysql.connector
import MySQLdb
import urllib2
from crawler import Crawler
from pymongo import MongoClient
from time import sleep
from kazoo.client import KazooClient
import os

# reload sys in order to deal with char set
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# start ZooKeeper Cluster
hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
zk = KazooClient(hosts = hosts_list)
zk.start()

# try to use many kinds of MySQL Client to kill the fu*king BUG

#db2 = pymysql.connect(host="localhost",user="root",passwd="765885195",db="HP",charset="utf8")
#db2 = mysql.connector.connect(user="root", passwd="765885195", database="HP", use_unicode=True)
#db2 = MySQLdb.connect("localhost", "root", "765885195", "HP")
db1 = MySQLdb.connect(host="localhost",user="root",passwd="765885195",db="HP",charset="utf8")
db2 = MySQLdb.connect(host="localhost",user="root",passwd="765885195",db="HP",charset="utf8")

instant_data = ["35"]

# 支持的网站信息
info = {'0':['www.taobao.com','1'],#
        '1':['www.tmall.com','1'],
        '2':['www.jd.com','1'],
        '3':['www.cnblogs.com','2'],
        '4':['blog.csdn.net','2'],
        '5':['blog.sina.com.cn','2'],
        '6':['blog.51cto.com','2'],
        '7':['www.chinanews.com','3'],
        '8':['www.chinadaily.com.cn','3'],
        '9':['www.eastday.com','3'],
        '10':['www.huanqiu.com','3'],
        '11':['news.sina.com.cn','3'],
       }

info_zk = {'0':['taobao','1'],     #
        '1':['tmall','1'],         #
        '2':['jingdong','1'],
        '3':['cnblog','2'],
        '4':['csdnblog','2'],      #
        '5':['sinablog','2'],
        '6':['ctoblog','2'],
        '7':['chinanews','3'],
        '8':['chinadaily','3'],
        '9':['eastnews','3'],
        '10':['huanqiunews','3'],
        '11':['sinanews','3'],    #
       }      

state_map = {"5":"continue", "8":"pause", "13":"stop"}
node_map = {}

# MongoDB handle (Mongodb连接句柄)
mdb = []
# 展示数据
show_data = []

def Saveto_mysql():
    ip_list = []
    sql = "select * from info"
    try:
        cur = db1.cursor()
        cur.execute(sql)
        db1.commit()
        result = cur.fetchall()
        
        for field in result:
            ip_list.append(field[1])
        del result
        cur.close()
        print ip_list
    except Exception, e:
        print "Error: %s" % e

    num = len(mdb)

    for i in range(num):
        tip = ip_list[i].split('.')
        db_name = ""
        for t in tip:
            db_name += t
        ip_list[i] = MongoClient(ip_list[i], 27017)
        mdb.append(ip_list[i][db_name])

    while True:
        num = len(mdb)
        collections = []
        tsql = "select url,keywords,genre from task group by url,keywords,genre"
        try:
            cur = db1.cursor()
            cur.execute(tsql)
            db1.commit()
            result = cur.fetchall()
        
            for task in result:
                print '任务: ', task[0], task[1]
                li = []
                li.append(task[0])
                li.append(task[1])
                li.append(task[2])
                collections.append(li)
                print '当前collection: ', collections
            del result
            cur.close()
        except Exception, e:
            print "HP said Error: %s" % e
            #sys.exit(0)
   
        print '总collections: ', collections

        for i in range(len(collections)):
            sum = 0
            coll_name = info[collections[i][0]][0]
            print '当前任务链接: ', coll_name
            if coll_name == 'blog.51cto.com':
                coll_name = 'ctoblog'
            keywords = collections[i][1]
            genre = collections[i][2]

            if not keywords:
                for j in range(num):
                    try:
                        sum += mdb[j][coll_name].count()
                    except Exception,e:
                        pass
            else:
                for j in range(num):
                    sum += mdb[j][keywords].count()
            str_sql = "insert into amount values('"+str(collections[i][0])+"', '"+str(keywords)+"', "+str(sum)+", '"+str(genre)+"', now())"
            print str_sql
            try:
                cur = db1.cursor()
                cur.execute(str_sql)
                db1.commit()
                result = cur.fetchall()
                del result
                cur.close()
            except Exception, e:
                print "Error: %s" % e
        sleep(10)


def drop_data(url, keywords):
    coll_name = info[url][0]
    if not keywords:
        print coll_name
        print mdb
        for client in mdb:
            client[coll_name].remove({})
    else:
        for client in mdb:
            client[keywords].remove({})

def send_data(url, keywords):
    data_num = []
    num = len(mdb)
    coll_name = info[url][0]
    genre = info[url][1]

    # 找出爬取数据最多的机子
    for i in xrange(num):
        data_num.append(mdb[i][coll_name].count())
    max_num = max(data_num)
    client = mdb[data_num.index(max_num)]

    # 随机选取数据
    if max_num > 100:
        random_num = random.randint(0, max_num-100)
    else:
        random_num = 0

    if not keywords:
        coll = client[coll_name]
    else:
        coll = client[keywords]
    print 'genre: ', genre
    # 电商
    if genre == '1':
        print "正在获取电商数据......"
        # 在爬取数据最多的机子上获取指定数目的数据
        result = coll.find().skip(random_num).limit(30)
        for res in result:
            show_data.append(res['link'])
            show_data.append(res['title'])
            show_data.append(res['price'])
            show_data.append(res['shop'])
            show_data.append(res['shopLink'])
            try:
                compositeScore = str((float(res['serviceScore'])+float(res['describeScore'])+float(res['logisticsScore']))/3)[:3]
            except Exception, e:
                compositeScore = '尚未收到评价'
            show_data.append(compositeScore)
    else:
        # 在爬取数据最多的机子上获取指定数目的数据
        print 'i am here'
        print coll
        result = coll.find().skip(random_num).limit(4)
        for res in result:
            tdata = "原文链接:  " + res['url'] + "\n\n标题:  " + res['title'].strip() + "\n\n发布时间:  " + res['releaseTime'] + "\n\n类别:  " + str(res['sort']) + "\n\n标签:  " + str(res['tags']) + "\n\n阅读人数:  " + str(res['readnum']) + "\n\n正文: \n\n" + str(res['article']).strip() + "\n\n"
            show_data.append(tdata)
            show_data.extend(['','','','',''])


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def get_ready_node(self, priority):
        ready_list = []
        for i in range(priority):
            task_num_max = 9999                           
            for node in node_map:
                if node_map[node][1] == '21' and node_map[node][2] < task_num_max and node not in ready_list:
                    obj_node = node
                    task_num_max = node_map[node][2]
            ready_list.append(obj_node)
        return ready_list

    def handle(self):
        print self.request.getpeername()
        while True:
            try:
                data = self.request.recv(1024)
                print data
                jdata = json.loads(data)
            except Exception, e:
                print "正在等待主控发来指令...."
                break
            
            # request to show working job
            # 请求正在运行任务
            #url+ '' ['1']
            if jdata[0]['Agreement'] == '1':
                print 'mt请求正在运行任务....'
                task = ['1']
                sql = "select * from task where status='5' or status='8'"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()
                    for res in result:
                        task.append(res[0])
                        task.append(res[1])
                        task.append(res[2])
                        task.append(res[3])
                        task.append(res[4].strftime("%Y-%m-%d %H:%M:%S"))
                        task.append(res[5])
                    print "$$$"
                    print  task
                    del result
                    cur.close()
                except Exception, e:
                    print "get working task SQL Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "get working task Send error: %s" % e

            # request tp show all job(include history job)
            # 获取所有任务
            elif jdata[0]['Agreement'] == '2':
                print 'mt请求所有任务....'
                task = ['2']
                sql = "select * from task"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[1])

                    del result
                    cur.close()

                except Exception, e:
                    print "get all task SQL Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "get all task Send error: %s" % e

            # request to show end job
            # 获取终止任务 
            elif jdata[0]['Agreement'] == '3':
                print 'mt请求所有任务....'
                task = ['3']
                sql = "select * from task where status='13'"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[2])
                    
                    del result
                    cur.close()

                except Exception, e:
                    print "get end task SQL Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "get end task Send Error: %s" % e

            # request to start a job (multi URL)
            # 混合url任务请求
            elif jdata[0]['Agreement'] == '4':
                urls = jdata[0]['Content'].split(', ')
                print 'urls', urls
                priority = int(urls[len(urls)-1])
                for i in range(len(urls)-1):
                    url = str(urls[i])
                    task_type = info_zk[url][0]
                    ready_list = self.get_ready_node(priority)

                    for j in range(priority):
                        print ready_list[j] + "&&&"
                        zk.set("/command/" + ready_list[j], value = task_type)
                        node_map[ready_list[j]][2] += 1 # task_num++
                    temp_list = zk.get_children("/signal/" + task_type)
                    for i in temp_list:
                        zk.delete('/signal/' + task_type + '/' +str(i))
                    zk.create("/signal/" + task_type + '/start')
                    for ready_node in ready_list:
                        sql = "insert into task values('"+url+"','','"+info[url][1]+"',"+ready_node+",now(),'5')"
                        nsql = "update info set tasknum=tasknum+1 where id='" + ready_node + "'"
                        try:
                            cur = db2.cursor()
                            cur.execute(sql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                        except Exception, e:
                            sql = "update task set status='5' where url='" + url + "' and keywords=''"
                            cur = db2.cursor()
                            cur.execute(sql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                        try:
                            cur = db2.cursor()
                            cur.execute(nsql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                            cur.close()
                        except Exception, e:
                            print "start task(multi) SQL Error: %s" % e
                    
                        # 发布任务后在amount表中插入20条空数据，防止出现时间倒序
                        tsql = "insert into amount values('"+url+"','',0,'"+info[url][1]+"',now())"
                        for i in range(20):
                            try:
                                cur = db2.cursor()
                                cur.execute(tsql)
                                db2.commit()
                                result = cur.fetchall()
                                del result
                                cur.close()
                            except Exception, e:
                                print 'insert amount(indistinct) execute error: ', e

                print priority
                print type(priority)
                try:
                    self.request.sendall(json.dumps(["4","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["4","-1"]))
                    print "start task(multi) Send error: %s" % e
            
            # request to start a single URL job
            # 发布精确任务
            elif jdata[0]['Agreement'] == '5':
                urls = jdata[0]['Content'].split(', ')
                print 'urls', urls
                url = str(urls[0])
                keyword = urls[1]
                priority = int(urls[2])
                task_type = (info_zk[url][0] + '_' + keyword).decode("utf-8")

         
                ready_list = self.get_ready_node(priority)
                for i in range(priority):
                    zk.set("/command/" + ready_list[i], value = task_type.encode("utf-8"))
                    node_map[ready_list[i]][2] += 1 # task_num++
                if zk.exists("/signal/" + task_type) != None:
                    temp_list = zk.get_children("/signal/" + task_type)
                    for i in temp_list:
                        zk.delete('/signal/' + task_type + '/' +str(i))
                else:
                    zk.create("/signal/" + task_type)
                    
                zk.create("/signal/" + task_type + '/start')
                for ready_node in ready_list:
                    print type(keyword)
                    sql = "insert into task values('"+url+"', '"+keyword+"','"+info[url][1]+"',"+str(ready_node)+",now(),'5')"
                    nsql = "update info set tasknum=tasknum+1 where id='" + ready_node + "'"
                    try:
                        cur = db2.cursor()
                        cur.execute(sql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    except Exception, e:
                        sql = "update task set status='5' where url='" + url + "' and keywords='" + keyword + "'"
                        cur = db2.cursor()
                        cur.execute(sql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    
                    try:
                        cur = db2.cursor()
                        cur.execute(nsql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    except Exception, e:
                        print "start task(acc) SQL Error: %s" % e



                    # 发布任务后在amount表中插入20条空数据，防止出现时间倒序
                    tsql = "insert into amount values('"+url+"','"+ keyword+"',0,'"+info[url][1]+"',now())"
                    for i in range(20):
                        try:
                            cur = db2.cursor()
                            cur.execute(tsql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                            cur.close()
                        except Exception, e:
                            print 'insert amount(accurate) execute error: ', e

                try:
                    self.request.sendall(json.dumps(["5","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["5","-1"]))
                    print "start task(acc) Send error: %s" % e

            # request to start a job instantly
            # 发布即时任务
            elif jdata[0]['Agreement'] == '8':
                del instant_data[:]
                instant_data.append('35')
                try:
                    self.request.sendall(json.dumps(["8","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["8","-1"]))
                    print "start im task Send error: %s" % e
                try:
                    urls = jdata[0]['Content'].split(', ')
                    for url in urls:
                        if not url.startswith('http'):
                            url = "http://" + url
                        if url.endswith('com') or url.endswith('net'):
                            url = url + "/"
                        crawl = Crawler(url)
                        if re.search('taobao|jiyoujia', url):
                            instant_data.append(url)
                            instant_data.append("1")
                            instant_data.append(str(crawl.spider_taobao()))
                        elif re.search('tmall', url):
                            instant_data.append(url)
                            instant_data.append("1")
                            instant_data.append(str(crawl.spider_tmall()))
                        elif re.search('jd.com', url):
                            instant_data.append(url)
                            instant_data.append("1")
                            instant_data.append(str(crawl.spider_jingdong()))
                        elif re.search('blog.sina', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_sinablog())
                        elif re.search('csdn', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_csdnblog())
                        elif re.search('news.sina', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_sinanews())
                        elif re.search('chinanews', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_chinanews())
                        else:
                            try:
                                urllib2.urlopen(url).read()
                            except Exception:
                                instant_data.append(url)
                                instant_data.append("0")
                                instant_data.append("链接有误，请检查后重新输入!!!")
                            else:
                                instant_data.append(url)
                                instant_data.append("0")
                                instant_data.append("目前不支持!!!")

                    print instant_data
                except Exception, e:
                    print "start im task Error: %s" % e

            # change job state(pause, continue,)
            # 修改任务状态
            elif jdata[0]['Agreement'] == '9':
                obj_list = []
                data = jdata[0]['Content'].split(',')
                sql = "select id from task where url='" + data[0] + "' and keywords='" + data[1] + "'"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()

                    for field in result:
                        obj_list.append("%010d" % field[0])
                    del result
                    cur.close()
                except Exception, e:
                    print "change task state SQL(select) Error: %s" % e
                task_state = state_map[str(data[2])]
                task_type =  info_zk[str(data[0])][0]
                task_keyword = str(data[1])

                if task_keyword != '':
                    task_type = task_type + '_' + task_keyword
                print task_type
                temp_list = zk.get_children("/signal/" + task_type)
                for i in temp_list:
                    zk.delete('/signal/' + task_type + '/' +str(i))

                zk.create('/signal/' + task_type + '/' + task_state)
                if task_state == "stop":
                    sql = "update task set status='13' where url='" + data[0] + "' and keywords='" + data[1] + "'"
                    
                    #sql = "delete from task where url='" + data[0] + "' and keywords='" + data[1] + "'"

                    try:
                        cur = db2.cursor()
                        cur.execute(sql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    except Exception, e:
                        print "change task state SQL(delete) Error: %s" % e

                    for obj_node in obj_list:
                        if node_map[obj_node][2] > 0:
                            node_map[obj_node][2] -= 1
                        else:
                            node_map[obj_node][2] = 0
                        nsql = "update info set tasknum=" + str(node_map[obj_node][2]) + " where id='" + obj_node + "'"
                    try:
                        cur = db2.cursor()
                        cur.execute(nsql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    except Exception, e:
                        print "change task state SQL(tasknum--) Error: %s" % e

                sql = "update task set status = '"+str(data[2])+"' where url='"+str(data[0])+"' and keywords='" + str(data[1]) + "'"
                
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()
                    del result
                    cur.close()
                except Exception, e:
                    print "change task state SQL(update) Error: %s" % e
                try:
                    self.request.sendall(json.dumps(["9","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["9","-1"]))
                    print "change task state Send error: %s" % e
            
            # request to show jobs and down nums
            # 获取任务及下载总数
            elif jdata[0]['Agreement'] == '13':
                print 'mt请求任务及下载总数....'
                task = ['13']
                sql = "select url,keywords,max(total) from amount group by url,keywords"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[1])
                        task.append(field[2])

                    del result
                    cur.close()
                except Exception, e:
                    print "get task amount SQL Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "get task amount Send error: %s" % e
            
            # request to show data log 
            # 查看数据日志
            elif jdata[0]['Agreement'] == '21':
                print '正在查看数据日志'
                log = ['21']
                data = jdata[0]['Content'].split(', ')
                #tsql = "select count(1) from amount"
                #cur = db2.cursor()
                #cur.execute(tsql)
                #num = cur.fetchall()[0][0]
                #if num < 10:
                #    sql = "select * from amount where url='" + str(data[0]) + "' and keywords='" + str(data[1]) + "'"
                #else:
                #sql = "select * from amount where time in (select time from (select * from amount where url='"+str(data[0])+"' and keywords='"+str(data[1])+"' order by time desc limit 10) as tp)"
                sql = "select * from amount where url='"+str(data[0])+"' and keywords='"+str(data[1])+"' order by time desc limit 10"
                print sql
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()

                    for field in result:
                        log.append(field[2])
                        #log.append(field[4].strftime("%m/%d %H:%M:%S"))
                        log.append(field[4].strftime("%H:%M:%S"))
                    print log
                    del result
                    cur.close()

                except Exception, e:
                    print "get log SQL Error: %s" % e
                try:
                    self.request.sendall(json.dumps(log))
                except Exception, e:
                    print "get log Send error: %s" % e
    
            # request to show history job down nums
            # 获取任务下载总数
            elif jdata[0]['Agreement'] == '34':
                print 'mt请求历史任务下载总数....'
                task = ['34']
                esql = "select sum(total) from (select url,keywords,genre,max(total) as total from amount where genre='1' group by url,keywords,genre) as tp"
                bsql = "select sum(total) from (select url,keywords,genre,max(total) as total from amount where genre='2' group by url,keywords,genre) as tp"
                nsql = "select sum(total) from (select url,keywords,genre,max(total) as total from amount where genre='3' group by url,keywords,genre) as tp"
                
                print esql
                print bsql
                print nsql
                try:
                    cur = db2.cursor()
                    cur.execute(esql)
                    db2.commit()
                    result_esum = cur.fetchall()
                    cur.execute(bsql)
                    db2.commit()
                    result_bsum = cur.fetchall()
                    cur.execute(nsql)
                    db2.commit()
                    result_nsum = cur.fetchall()
                    if result_esum[0][0] is None:
                        task.append(0)
                    else:
                        task.append(int(result_esum[0][0]))
                    if result_bsum[0][0] is None:
                        task.append(0)
                    else:
                        task.append(int(result_bsum[0][0]))
                    if result_nsum[0][0] is None:
                        task.append(0)
                    else:
                        task.append(int(result_nsum[0][0]))

                    print task
                    del result_esum
                    del result_bsum
                    del result_nsum
                    cur.close()

                except Exception, e:
                    print "get down data sql Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "get down data Send error: %s" % e
           
            # 发送即时任务数据
            elif jdata[0]['Agreement'] == '35':

                try:
                    if not instant_data:
                        self.request.sendall(json.dumps(['35']))
                    else:
                        self.request.sendall(json.dumps(instant_data))
                except Exception, e:
                    print "send im dataSend error: %s" % e
            
            # 数据展示
            elif jdata[0]['Agreement'] == '36':

                data = jdata[0]["Content"].split(', ')
                del show_data[:]
                print data
                show_data.append('36')
                t = threading.Thread(target=send_data, args=(data[0], data[1]))
                t.start()
                sleep(3) 
                
                try:
                    self.request.sendall(json.dumps(show_data))
                except Exception, e:
                    print "send show_data error: %s" % e


            elif jdata[0]['Agreement'] == '55':  # refresh node state
                print 'mt请求从机资源....'
                resource_info = ['55']

                for node in node_map:
                    if zk.exists("/command/" + node) != None:
                        node_map[node][1] = '21' # alive-working
                        sql = "update info set status='21' where id='" + node + "'"
                        try:
                            cur = db2.cursor()
                            cur.execute(sql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                            cur.close()
                        except Exception, e:
                            print "refresh node SQL Error: %s" % e
                    elif node_map[node][1] == '21':
                        node_map[node][1] = '34' # dead
                        sql = "update info set status='34' where id='" + node + "'"
                        tsql = "update info set tasknum=0 where id='" + node + "'"
                        try:
                            cur = db2.cursor()
                            cur.execute(sql)
                            result = cur.fetchall()
                            del result
                            cur.execute(tsql)
                            db2.commit()
                            result = cur.fetchall()
                            del result
                            cur.close()
                        except Exception, e:
                            print "refresh node SQL Error: %s" % e

                    resource_info.append(node)
                    resource_info.append(node_map[node][0])
                    resource_info.append(node_map[node][1])
                    resource_info.append(node_map[node][2])

                try:
                    print resource_info
                    print json.dumps(resource_info)
                    self.request.sendall(json.dumps(resource_info))
                except Exception, e:
                    print "refresh node Send error: %s" % e
           
            
            elif jdata[0]['Agreement'] == '56':  # change node state
                data = jdata[0]["Content"].split(',')
                sql = "update info set status = '" + data[1] + "' where id = '" + data[0] + "'"
                tsql = "update task set status='13' where id='" + data[0] + "'"
                #tsql = "delete from task where id='" + data[0] + "'"
                if data[1] == '55':              # stop a node
                    zk.set("/command/" + data[0], value = "stop")
                    zk.delete("/command/" + data[0])
                    node_map[data[0]][1] = '34'  # node is over
                    node_map[data[0]][2] = 0
                else:                            # start a node
                    obj_ip = node_map[data[0]][0]
                    print "^^^^" + data[0]
                    cmd = "ssh root@{} 'python /root/V3/project/run.py {} 1>log' &".format(obj_ip, "%010d" % int(data[0]))
                    os.system(cmd)
                    node_map[data[0]][1] = '21'  # node is working 
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()
                    del result
                    cur.execute(tsql)
                    db2.commit()
                    result = cur.fetchall()
                    del result
                    cur.close()
                except Exception, e:
                    print "Change node state: %s" % e
   
                try:
                    self.request.sendall(json.dumps(["56","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["56","-1"]))
                    print "Change node Send error: %s" % e
            

            elif jdata[0]['Agreement'] == '57': # delete / add a node 
                data = jdata[0]["Content"].split(',')
                ip = data[1]
                

                if data[0] == "0":              # delete a node
                    sql = "delete from info where id = '" + data[1] + "'"
                    # tsql = "update task set status='13' where id='" + data[1] + "'"

                    node_map.pop(data[1])
                    try:
                        cur = db2.cursor()
                        cur.execute(sql)
                        #cur.execute(tsql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()

                    except Exception, e:
                        print "delete SQL Error: %s" % e
                elif data[0] == "1": 
                    # 将Mongodb2连接句柄追加到全局列表中
                    tip = ip.split('.')
                    db_name = ""
                    for t in tip:
                        db_name += t
                    client = MongoClient(ip, 27017)
                    mdb.append(client[db_name])
                    
                    sql = "insert into info values(null,'" + data[1] + "','55',0)"
                    try:
                        cur = db2.cursor()
                        cur.execute(sql)
                        db2.commit()
                        result = cur.fetchall()
                        del result
                        cur.close()
                    except Exception, e:
                        print "add SQL Error: %s" % e

                    tsql = "select max(id) from info"
                    try:
                        cur = db2.cursor()
                        cur.execute(tsql)
                        db2.commit()
                        result = cur.fetchall()
                        cur.close()
                    except Exception, e:
                        print "add-query node: %s" % e
                    
                    node_name = "%010d" % result[0][0]
                    node_map[node_name] = list((ip, '55', 0)) 
                    del result
                

                try:
                    self.request.sendall(json.dumps(["57","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["57","-1"]))
                    print "add / delete Send error: %s" % e

            # delete data 
            # 删除数据
            elif jdata[0]['Agreement'] == '89':
                data = jdata[0]["Content"].split(',')
                sql = "delete from amount where url='"+data[0]+"' and keywords='"+data[1]+"'"
                try:
                    cur = db2.cursor()
                    cur.execute(sql)
                    db2.commit()
                    result = cur.fetchall()
                    del result
                    cur.close()
                except Exception, e:
                    print "delete data SQL Error: %s" % e

                
                # 删除Mongodb2数据
                mt = threading.Thread(target=drop_data, args=(data[0], data[1]))
                mt.start()

                try:
                    self.request.sendall(json.dumps(["89","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["89","-1"]))
                    print "delete data Send error: %s" % e

def sigint_handler(signum, frame):
    print 'catched interrupt signal!'

# get data in DB to memory 
def mysql_to_memory():
    sql = "select * from info"
    try:
        cur = db2.cursor()
        cur.execute(sql)
        db2.commit()
        result = cur.fetchall()
        for field in result:
            node_map["%010d" % field[0]] = list((field[1], field[2], field[3]))
        del result
        cur.close()
    except Exception, e:
        print "mysql_to_memory SQL Error: %s" % e   

if __name__ == "__main__":
    

    signal.signal(signal.SIGINT, sigint_handler)

    mysql_to_memory()
    
    HOST, PORT = "172.18.214.188", 8888 # Server IP address and port
    
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.ThreadingTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    print "waiting for connection....."

    # save data num to mysql
    t = threading.Thread(target=Saveto_mysql,args=())
    t.start()
 
    server.serve_forever()

