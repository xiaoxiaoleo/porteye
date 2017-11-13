# encoding:utf-8
# code by evileo

'''
Created on 2016 

@author: evileo
'''
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
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','porteye.settings')
 
import django
django.setup()
from portmonitor.models import checktask 
# from setting.models import server_setting


from hconfig import cpath,xpython,master_server,masscan_dir

#from libs.simple_shedule import run as s_run() #run(interval, command)

from subprocess import Popen

import xmltodict



import  datetime,time

from libs.mylogger import mylogger
logger = mylogger('check masscan.py')


from libs.utils import postHttp,sort_masscan
def main(ip_addr,project_id):
    logger.info('checkmasscantasking')
    try:
        cmd =  "sudo " + masscan_dir +"bin/masscan --ports 1-65535  " + ip_addr +" --max-rate 3000  --source-port 60000 -oX /tmp/scanoutput.xml" 
        logger.info(cmd)
        proc = Popen(cmd.split(),shell=False,cwd=masscan_dir).wait()
        try:
            f = open("/tmp/scanoutput.xml")
        except:
            return

        parsed_file_data = xmltodict.parse(f)
        tmp_list = []
        for element in parsed_file_data['nmaprun']['host']:
            tmp_list.append('{}:{}'.format(element['address']['@addr'],element['ports']['port']['@portid'])) 

        sort_dic =  sort_masscan(tmp_list)

        for _ip  in sort_dic:
            _all_ports = '-'.join(sort_dic[_ip])
            logger.info(_all_ports)
            serverurl = 'http://'+master_server+'/portmonitor/uploadopenport'
            #{u'domain': [u'172.32.1.100'], u'project_id': [u'271'], u'data': [u'33147-22147-63886-30147-6379-21147']}
            logger.info(serverurl)  

            data = {'domain':_ip,'project_id':project_id,'data': _all_ports}
            logger.info(data)
            postHttp(serverurl ,data)
            time.sleep(1)


    
    except Exception,e:
        logger.error(e)
        #continue
        return


def test():
    #cmd = "sudo /home/leo/Desktop/porteye/masscan/bin/masscan --ports 1-65535  172.32.1.147 --max-rate 3000  --source-port 60000 -oX /tmp/scanoutput.xml"
    # cmd ='whoami'
    # #logger.info(cmd)
    # print cmd
    # proc = Popen(cmd.split(),shell=False,cwd=masscan_dir).wait()
    serverurl = 'http://'+master_server+'/portmonitor/uploadopenport'

    #{u'domain': [u'172.32.1.100'], u'project_id': [u'271'], u'data': [u'33147-22147-63886-30147-6379-21147']}
    logger.info(serverurl)  

    data = {'domain':'127.0.0.1','project_id':333,'data': '49666-9421-15485-445-902-62806-65412-65325-49665-49182-65453-9088-9088-49668-49669-912-23401-135-49664-65452-49667'}

    logger.info(data)
    postHttp(serverurl ,data)


def usage():
    print """
    masscan.py ip_addr    project_id 
    """

if __name__ == '__main__':

    if len(sys.argv) != 3:
        #test()
        usage()
        sys.exit(-1)
        
    ip_addr = sys.argv[1]
    project_id =  sys.argv[2]
    main(ip_addr,project_id)
    #test()

