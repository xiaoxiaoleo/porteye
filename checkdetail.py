# encoding:utf-8
# copy by evileo


import urllib2
import urllib
import sys
import argparse
import django
import logging
import requests
import json 
import os
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sslcloud.settings')
 
import django
django.setup()
from sslcheck.models import checktask 
from hconfig import cpath,xpython,master_server,masscan_dir,wyportmap_dir
from checkmail import check_sendmail 
from subprocess import Popen
import xmltodict
from portmonitor.models import OpenPort,ResultPorts
import  datetime,time
from libs.mylogger import mylogger
logger = mylogger('check masscan.py')
from libs.utils import postHttp,list_str2int,list_int2str
from hconfig import cpath,xpython,master_server,masscan_dir
 



def run_fnascan(project_id,ip_addr,_open_port):
    #####run fnascan 
    logger.info("FNASCAN PORT : "+str(_open_port))
    need_scan_port = ','.join(list_int2str(_open_port))
    jsonfilename = ip_addr + '.html'
    os.chdir(cpath + 'fnascan/')
    cmd = xpython + ' ' + cpath + 'fnascan/fnascan.py  -h ' + ip_addr  + ' -p ' +need_scan_port
    logger.info(cmd)  
    os.system(cmd)
    try:
        ff = open('./'+jsonfilename)
        postdata = ff.read()
    except:
        postdata = {} 
    data = {'domain':ip_addr,'project_id':project_id,'data':postdata}
    try:
        ff.close() 
        os.remove('./'+jsonfilename) 
    except:
        pass
    os.chdir(cpath)
    serverurl = 'http://'+master_server+'/portmonitor/uploadfnascanresult'
    logger.info(serverurl)  
    postHttp(serverurl ,data)


def run_wyportmap(project_id,ip_addr,port_list):
    logger.info("PORT FROM OpenPort : "+str(port_list))
    default_need_scan = ['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
    for  p in port_list:
        if p not in default_need_scan:
            default_need_scan.append(p)

    ###run wyport map
    need_scan_port = ','.join(default_need_scan)
    logger.info("PORT WILL WYPORTMAP SCAN : "+need_scan_port)
    try:
        cmd =  "sudo " +  xpython + ' ' +'   '+ wyportmap_dir+'  ' + ip_addr + '  ' +need_scan_port + '  ' +  str(project_id) 
        logger.info(cmd)
        proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()
    except Exception,e:
        logger.error(e)
        pass


def scan_single_ip(ip_addr,project_id = 0):
    if not project_id:
        project_id = OpenPort.objects.values_list('project_id',flat=True).filter(ip=ip_addr).distinct()[0]
    port_list = OpenPort.objects.values_list('port',flat=True).filter(ip=ip_addr,port_status=1)
    #port_list  = list_str2int(port_list)
    run_wyportmap(project_id = project_id,ip_addr = ip_addr ,port_list =  port_list)
    #get wyportmap open portlist,then push to /portmonitor/uploadopenport
    _open_port = []
    try:
        newest_insert_time = ResultPorts.objects.filter(address = ip_addr).values_list('inserted',flat=True).order_by('-inserted')[0]
        _open_port = ResultPorts.objects.filter(inserted = newest_insert_time).values_list('port',flat=True).distinct()
    except Exception,e:
        logger.error(e)
        pass
    _open_port = list_int2str(_open_port)
    _all_ports  = '-'.join(_open_port)
    data = {'domain':ip_addr,'project_id':project_id,'data': _all_ports}
    logger.info(data)
    serverurl = 'http://'+master_server+'/portmonitor/uploadopenport'
    postHttp(serverurl ,data)
    

    run_fnascan(project_id = project_id,ip_addr = ip_addr,_open_port = _open_port)


def main():
    #while True:
    allip =OpenPort.objects.values_list('ip',flat=True).order_by('last_checkdetail_time').distinct()
    task_length = len(allip)
    #['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
    logger.info('checkdetail.py')
    for i in range(0,task_length):
        ip_addr = allip[i]

        scan_single_ip(ip_addr = ip_addr)



def usage():
    print """
    checkdetall.py ip_addr    project_id 
    """      

def test_uploadopenport():
    #cmd = "sudo /home/leo/Desktop/sslcloud/masscan/bin/masscan --ports 1-65535  172.32.1.147 --max-rate 3000  --source-port 60000 -oX /tmp/scanoutput.xml"
    # cmd ='whoami'
    # #logger.info(cmd)
    # print cmd
    # proc = Popen(cmd.split(),shell=False,cwd=masscan_dir).wait()
    data = {'domain':'x.x.x.x', 'project_id': '1', 'data': '80-427-443-902-5989-8000-8100'}

    serverurl = 'http://'+master_server+'/portmonitor/uploadopenport'
    postHttp(serverurl ,data)


def test_uploadfnascan():
    run_fnascan(1,'x.x.x.x', ['22', '80', '443', '1883', '18301'])

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 3:
        scan_single_ip(sys.argv[1],sys.argv[2])
        
    else:
        usage()
        sys.exit(-1)
    #test()
    #test_uploadfnascan()
