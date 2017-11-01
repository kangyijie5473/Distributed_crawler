#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import SocketServer
import re
import json
import signal
import pymysql
from crawler import Crawler
from pymongo import MongoClient
from time import sleep
from kazoo.client import KazooClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
zk = KazooClient(hosts = hosts_list)
zk.start()
db = pymysql.connect(host="localhost",user="root",passwd="765885195",db="Distributed",charset="utf8")

instant_data = ["35"]

# 支持的网站信息
info = {'0':['www.taobao.com','1'],
        '1':['www.tmall.com','1'],
        '2':['www.jd.com','1'],
        '3':['www.suning.com','1'],
        '4':['www.gome.com','1'],
        '5':['www.amazon.cn','1'],
        '6':['www.dangdang.com','1'],
        '7':['www.cnblogs.com','2'],
        '8':['blog.csdn.net','2'],
        '9':['blog.sina.com.cn','2'],
        '10':['blog.51cto.com','2'],
        '11':['blog.hexun.com','2'],
        '12':['www.chinanews.com','3'],
        '13':['www.chinadaily.com.cn','3'],
        '14':['www.eastday.com','3'],
        '15':['www.huanqiu.com','3'],
        '16':['news.sina.com.cn','3'],
       }
info_zk = {'0':['taobao','1'],
        '1':['www.tmall.com','1'],
        '2':['jingdong','1'],
        '3':['suning','1'],
        '4':['gome','1'],
        '5':['amazon','1'],
        '6':['dangdang','1'],
        '7':['cnblog','2'],
        '8':['csdnblog','2'],
        '9':['sinablog','2'],
        '10':['ctoblog','2'],
        '11':['hexunblog','2'],
        '12':['chinanews','3'],
        '13':['chinadaily','3'],
        '14':['eastnews','3'],
        '15':['huanqiunews','3'],
        '16':['sinanews','3'],
       }       

def Saveto_mysql():
    mdb = []
    ip_list = []
    
    sql = "select * from info"
    try:
        cur = db.cursor()
        cur.execute(sql)
        db.commit()
        result = cur.fetchall()
        
        for field in result:
            mdb.append(field[0])
            ip_list.append(field[1])

        print mdb
        print ip_list
    except Exception, e:
        print "Error: %s" % e

    num = cur.rowcount

    for i in range(num):
        ip_list[i] = MongoClient(ip_list[i], 27017)
        mdb[i] = ip_list[i][mdb[i]]
    
    while True:
        collections = {}
        tsql = "select * from task"
        try:
            cur = db.cursor()
            cur.execute(tsql)
            db.commit()
            result = cur.fetchall()
        
            for task in result:
                li = []
                li.append(task[1])
                li.append(task[2])
                collections[task[0]] = li
            print collections
        except Exception, e:
            print "Error: %s" % e
        
        for coll in collections.keys():
            sum = 0
            coll = info[coll][0]
            for i in range(num):
                sum += mdb[i][coll].count()
            str_sql = "insert into amount values('"+coll+"', '"+collections[coll][0]+"', "+sum+", '"+collections[coll][1]+"', now())"
            try:
                cur = db.cursor()
                cur.execute(str_sql)
                db.commit()
            except Exception, e:
                print "Error: %s" % e
        sleep(1)

def drop_data(url):
    mdb = []
    ip_list = []
    
    sql = "select * from info"
    try:
        cur = db.cursor()
        cur.execute(sql)
        db.commit()
        result = cur.fetchall()
        
        for field in result:
            mdb.append(field[0])
            ip_list.append(field[1])

        print mdb
        print ip_list
    except Exception, e:
        print "Error: %s" % e

    num = cur.rowcount

    for i in range(num):
        ip_list[i] = MongoClient(ip_list[i], 27017)
        mdb[i] = ip_list[i][mdb[i]]
    
    url = info[url][0]
    for coll in mdb:
        coll[url].remove()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
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
            
            # 请求正在运行任务
            #url+ '' ['1']
            if jdata[0]['Agreement'] == '1':
                print 'mt请求正在运行任务....'
                task = ['1']
                sql = "select * from task where status='5' or status='8'"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[1])
                        task.append(field[2])
                        task.append(field[3].strftime("%Y-%m-%d %H:%M:%S"))
                        task.append(field[4])

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "Send error: %s" % e

            # 获取所有任务(li shi ren wu)
            # server 
            elif jdata[0]['Agreement'] == '2':
                print 'mt请求所有任务....'
                task = ['2']
                sql = "select * from task"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[1])

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "Send error: %s" % e

            # 获取终止任务 
            # server
            elif jdata[0]['Agreement'] == '3':
                print 'mt请求所有任务....'
                task = ['3']
                sql = "select * from task where status='13'"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[2])

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    pass

            # 混合url任务请求
            # zk 
            elif jdata[0]['Agreement'] == '4':
                urls = jdata[0]['Content'].split(', ')
                print 'urls', urls
                for i in range(len(urls)-1):
                    url = str(urls[i])
                    sql = "insert into task values('"+url+"','','"+info[url][1]+"',now(),'5')"
                    # 模拟插入，最后要删掉这句tsql
                    #tsql = "insert into amount values('"+url+"','',1000,'"+info[url][1]+"',now())"
                    print sql
                    try:
                        cur = db.cursor()
                        cur.execute(sql)
                        #cur.execute(tsql)
                        db.commit()
                    except Exception, e:
                        print "Error: %s" % e
                    

                priority = urls[len(urls)-1]
                print priority
                print type(priority)
                try:
                    self.request.sendall(json.dumps(["4","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["4","-1"]))
                    print "Send error: %s" % e
            
            # 发布精确任务
            # zk
            elif jdata[0]['Agreement'] == '5':
                urls = jdata[0]['Content'].split(', ')
                print 'urls', urls
                url = str(urls[0])
                keyword = urls[1]
                sql = "insert into task values('"+url+"', '"+keyword+"','"+info[url][1]+"',now(),'5')"
                # 模拟插入，最后要删掉这句tsql
                #tsql = "insert into amount values('"+url+"','"+urls[1]+"',1000,'"+info[url][1]+"',now())"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    #cur.execute(tsql)
                    db.commit()
                except Exception, e:
                    print "Error: %s" % e
                priority = urls[2]
                print priority
                print type(priority)
                try:
                    self.request.sendall(json.dumps(["5","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["5","-1"]))
                    print "Send error: %s" % e

            # 发布即时任务
            # no
            elif jdata[0]['Agreement'] == '8':
                del instant_data[:]
                instant_data.append('35')
                try:
                    self.request.sendall(json.dumps(["8","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["8","-1"]))
                    print "Send error: %s" % e
                try:
                    urls = jdata[0]['Content'].split(', ')
                    for url in urls:
                        if not url.startswith('http'):
                            url = "http://" + url
                        crawl = Crawler(url)
                        if re.search('taobao', url):
                            instant_data.append(url)
                            instant_data.append("1")
                            instant_data.append(str(crawl.spider_taobao()))
                        elif re.search('blog.sina', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_sinablog())
                        elif re.search('blog.csdn', url):
                            instant_data.append(url)
                            instant_data.append("0")
                            instant_data.append(crawl.spider_csdnblog())
                    print instant_data
                except Exception, e:
                    print "Error: %s" % e

            # 修改任务状态
            # pause continue stop
            # to do  : continue time 
            elif jdata[0]['Agreement'] == '9':
                data = jdata[0]['Content'].split(',')
                sql = "update task set status = '"+str(data[2])+"' where url='"+str(data[0])+"' and keywords='" + str(data[1]) + "'"
                
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                except Exception, e:
                    print "Error: %s" % e
                try:
                    self.request.sendall(json.dumps(["9","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["9","-1"]))
                    print "Send error: %s" % e
            
            # 获取任务及下载总数
            # no
            elif jdata[0]['Agreement'] == '13':
                print 'mt请求任务及下载总数....'
                task = ['13']
                sql = "select url,keywords,max(total) from amount group by url,keywords"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        task.append(field[0])
                        task.append(field[1])
                        task.append(field[2])

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "Send error: %s" % e
            
            # 查看数据日志
            # no
            elif jdata[0]['Agreement'] == '21':
                print '正在查看数据日志'
                log = ['21']
                data = jdata[0]['Content'].split(', ')
                sql = "select * from amount where time in (select time from (select * from amount where url='"+str(data[0])+"' and keywords='"+str(data[1])+"' order by time desc limit 10) as tp)"
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        log.append(field[2])
                        #log.append(field[4].strftime("%m/%d %H:%M:%S"))
                        log.append(field[4].strftime("%H:%M:%S"))

                except Exception, e:
                    print "Error: %s" % e
                try:
                    self.request.sendall(json.dumps(log))
                except Exception, e:
                    print "Send error: %s" % e
    
            # 获取任务下载总数
            # no
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
                    cur = db.cursor()
                    cur.execute(esql)
                    db.commit()
                    result_esum = cur.fetchall()
                    cur.execute(bsql)
                    db.commit()
                    result_bsum = cur.fetchall()
                    cur.execute(nsql)
                    db.commit()
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

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print task
                    print json.dumps(task)
                    self.request.sendall(json.dumps(task))
                except Exception, e:
                    print "Send error: %s" % e
           
            # 发送即时任务数据
            elif jdata[0]['Agreement'] == '35':

                try:
                    if not instant_data:
                        self.request.sendall(json.dumps(['35']))
                    else:
                        self.request.sendall(json.dumps(instant_data))
                except Exception, e:
                    print "Send error: %s" % e
            
            # 请求从机peizhi
            # ren wu shu & state
            elif jdata[0]['Agreement'] == '55':
                print 'mt请求从机资源....'
                resource_info = ['55']
                sql = "select * from info"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    result = cur.fetchall()

                    for field in result:
                        resource_info.append(field[0])
                        resource_info.append(field[1])
                        resource_info.append(field[2])
                        resource_info.append(field[3])

                except Exception, e:
                    print "Error: %s" % e
                try:
                    print resource_info
                    print json.dumps(resource_info)
                    self.request.sendall(json.dumps(resource_info))
                except Exception, e:
                    print "Send error: %s" % e
           
            # ba si de nong cheng huo de 
            # dead -> alive
            # rpc
            elif jdata[0]['Agreement'] == '56':
                data = jdata[0]["Content"].split(',')
                sql = "update info set status = '" + data[1] + "' where id = '" + data[0] + "'"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                except Exception, e:
                    print "Error: %s" % e
                try:
                    self.request.sendall(json.dumps(["56","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["56","-1"]))
                    print "Send error: %s" % e
            
            # tian jia yi tai
            # list.append()
            elif jdata[0]['Agreement'] == '57':
                data = jdata[0]["Content"].split(',')
                if data[0] == "0":
                    sql = "delete from info where id = '" + data[1] + "'"
                elif data[0] == "1":
                    tsql = "select id from info"
                    t = []
                    try:
                        cur = db.cursor()
                        cur.execute(tsql)
                        db.commit()
                        result = cur.fetchall()
                        for field in result:
                            t.append(int(field[0][2:]))
                    except Exception, e:
                        print "Error: %s" % e
                    sql = "insert into info values('MT" +str(max(t)+1)+"', '"+data[1]+"','34',0)"
                print sql
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                except Exception, e:
                    print "Error: %s" % e
                try:
                    self.request.sendall(json.dumps(["57","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["57","-1"]))
                    print "Send error: %s" % e

            # 删除数据
            # no
            elif jdata[0]['Agreement'] == '89':
                data = jdata[0]["Content"].split(',')
                sql = "delete from amount where url='"+data[0]+"' and keywords='"+data[1]+"'"
                try:
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                except Exception, e:
                    print "Error: %s" % e

                try:
                    self.request.sendall(json.dumps(["89","0"]))
                except Exception, e:
                    self.request.sendall(json.dumps(["89","-1"]))
                    print "Send error: %s" % e
                
                # 删除Mongodb数据
                mt = threading.Thread(target=drop_data,args=(data[0],))
                mt.start()

def sigint_handler(signum, frame):
    print 'catched interrupt signal!'

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, sigint_handler)
    
    HOST, PORT = "172.18.214.188", 8888
    
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

