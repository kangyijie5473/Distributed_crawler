# -*- coding: utf-8 -*-
from kazoo.client import KazooClient
import os
import logging
import time
import signal
from multiprocessing import Process


main_dir = "/root/V3/project/"
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

signal_dir = '/signal/taobao' + '_' + sys.argv[1]
task_type = "accurate_taobao"
keyword = sys.argv[1]
def run_proc():
    os.chdir(main_dir +"accurate_taobao/accurate_taobao/spiders")
    #arg = ["HELLO","crawl", "spider_" + task_type,"--nolog"]
    arg = ["HELLO","crawl",  "spider_" + task_type, '-a',"keywords="+keyword]
    os.execvp("scrapy",arg)
def run_wait(a,b):
    try:
        os.waitpid(-1, os.WNOHANG)
    except Exception,e:
        print "no child"
signal.signal(signal.SIGCHLD, run_wait)


watchPid = [] 
for i in range(2,len(sys.argv)):
    watchPid.append(int(sys.argv[i]))

hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
signal_dic = {"stop":signal.SIGKILL, "start":signal.SIGCONT, "pause":signal.SIGSTOP, "continue":signal.SIGCONT}
zk = KazooClient(hosts = hosts_list)
logging.basicConfig()
zk.start()
try:
    zk.create(signal_dir)
except Exception:
    pass
print "watch dog working"
stop_flag = False

@zk.ChildrenWatch(signal_dir)
def signal_watch(children):
    if len(children) != 0:
        global watchPid
        for pid in watchPid:
            os.kill(pid, signal_dic[children[0]])
        if children[0] == "stop":
            global stop_flag
            stop_flag = True

def check(pid):
    global stop_flag
    if stop_flag == True:
        sys.exit(0)
    try:
     	os.kill(pid, 0) 
     	return pid
    except Exception:  #判断
        p = Process(target=run_proc)
        p.start()
        return p.pid
    	
while True:
    print "begin check"
    global stop_flag
    if stop_flag == True:
        sys.exit(0)

    for pid in watchPid:
        newpid = check(pid)
        if stop_flag == True:
            sys.exit(0)
        if newpid != pid:
        	print "new process"
        	watchPid.remove(pid)
        	watchPid.append(newpid)

    time.sleep(5)

