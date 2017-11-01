import os 
mydir =  os.getcwd()
os.system('./setup.sh')
cmd = "sed -i '11s#obj#" + mydir + "/#' ./launcher.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./taobao/taobao/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./csdnblog/csdnblog/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./cnblog/cnblog/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./ctoblog/ctoblog/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./chinanews/chinanews/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./chinadaily/chinadaily/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./huanqiunews/huanqiunews/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./hexunblog/hexunblog/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./suning/suning/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./jingdong/jingdong/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./sinablog/sinablog/watchdog.py"
os.system(cmd)
cmd = "sed -i '10s#obj#" + mydir + "/#' ./sinanews/sinanews/watchdog.py"
os.system(cmd)
