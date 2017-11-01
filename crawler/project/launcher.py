# -*- coding: utf-8 -*-
from scrapy import cmdline
import os
from kazoo.client import KazooClient
import time
from multiprocessing import Process
from random import randint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
main_dir = "/root/V3/project/"
def run_dog(pid_list,task_type):
    if '_' not in task_type:
        os.chdir(main_dir + task_type + '/' + task_type)
        arg = ["HELLO","watchdog.py"]
    else:
        task_type = task_type.split('_') 
        keyword = task_type[1]
        obj_dir = 'accurate_' + task_type[0]
        os.chdir(main_dir + obj_dir + '/' + obj_dir  )        
        arg = ["HELLO","watchdog.py", keyword]
    for pid in pid_list:
        arg.append(str(pid))
    os.execvp("python",arg)

def run_proc(num, task_type):
    if '_'  in task_type:
        task_type = task_type.split('_') 
        keyword = task_type[1]
        obj_dir = 'accurate_' + task_type[0]
        os.chdir(main_dir + obj_dir + '/' + obj_dir + "/spiders" )
        key = "keywords=" + keyword
        #print "^^" + key
        arg = ["HELLO","crawl", "spider_" + obj_dir, '-a', key, '--nolog']
        #arg = ["HELLO","crawl", "spider_" + obj_dir, '-a', key]
        os.execvp("scrapy",arg)
        #mystr = 'scrapy crawl spider_' + obj_dir + ' -a ' + key + ' --nolog'
        #print mystr
        #os.system(mystr)
    else:
        os.chdir(main_dir + task_type +'/' + task_type + "/spiders")
        arg = ["HELLO","crawl", "spider_" + task_type,"--nolog"]
        #arg = ["HELLO","crawl", "spider_" + task_type]
        os.execvp("scrapy",arg)
def run_blancer(task_type):
    os.chdir(main_dir + task_type +'/' + task_type )
    arg = ["HELLO","load_blancer.py"]
    os.execvp("python",arg)

hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
zk  = KazooClient(hosts = hosts_list)
zk.start()
task_type = sys.argv[1]
process_num = int(sys.argv[2])
signal_dir = "/signal/" + task_type
print signal_dir
try:
    zk.create(signal_dir.decode("utf-8"))
except Exception,e:
    print "error" 

pid_list = []
global stop_flag
stop_flag = False

@zk.ChildrenWatch(signal_dir.decode("utf-8"))
def signal_watch(children):
    if len(children) != 0 and children[0] == 'start':
        for i in range(process_num):
            p = Process(target=run_proc, args=(str(i),task_type))
            p.start()
            pid_list.append(str(p.pid))

        print pid_list
        dog = Process(target = run_dog, args =(pid_list, task_type))
        dog.start()
        #load_blancer = Process(target = run_blancer, args = (task_type, ))
        #load_blancer.start()
        for i in pid_list:
            pid_list.remove(i)
    if len(children) != 0 and children[0] == 'stop':
        global stop_flag
        stop_flag = True
        sys.exit(0)


while True:
    global stop_flag
    if stop_flag == True:
        sys.exit(0)

    try:
        os.waitpid(-1, 0)
    except Exception,e:
        print "no child"
    time.sleep(1)
time.sleep(100000)
