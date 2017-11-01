#!/usr/bin/env python
# coding=utf-8
from scrapy import cmdline
import os
import sys
from kazoo.client import KazooClient
import time
from multiprocessing import Process
from random import randint
import signal
main_dir = '/root/V3/project/'
def launcher(arg):
    os.execvp("python",arg)

if __name__ == '__main__':
    hosts_list =  ['123.206.89.123:2181', '123.207.157.135:2181', '118.89.234.46:2181']
    zk  = KazooClient(hosts = hosts_list)
    zk.start()

    command_dir = "/command/"
    if len(sys.argv) == 1:
        my_node =zk.create(command_dir + "", sequence = True, ephemeral = True, value = "empty")
    else:
        my_node =zk.create(command_dir + sys.argv[1], ephemeral = True, value = "empty")
       
    @zk.DataWatch(my_node)
    def command_watch(data, stat):  
        task_type = data
        print task_type
        if task_type != "empty":
            if task_type == "stop":
                os.kill(0, signal.SIGKILL)
            arg = ["hello",main_dir+"launcher.py",task_type,str(1)]
            task = Process(target = launcher, args = (arg, ))
            task.start()
            zk.set(my_node, value = "empty")

    time.sleep(100000)
