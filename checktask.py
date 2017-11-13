#!/usr/bin/env python
# encoding:utf-8

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
os.environ.setdefault('DJANGO_SETTINGS_MODULE','porteye.settings')
 
import django
django.setup()
 
from portmonitor.models import port_monitor

from hconfig import cpath,xpython 

#from libs.simple_shedule import run as s_run() #run(interval, command)

 

from libs.mylogger import mylogger
logger = mylogger('checktask.py')


from subprocess import Popen
def main():
 
    while(1):
        time.sleep(1)

        alltask =port_monitor.objects.all().order_by('id')
        task_length = len(alltask)
        
        for i in range(0,task_length):
            curobj = alltask[i]

            cmd =  xpython + ' ' + 'checkdetail.py'
            logger.info(cmd)   
            proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()


            cmd= cpath+'masscan.py '
            cmd =  xpython + ' ' + cmd  + '  '+  curobj.ip_range +'  ' +  str(curobj.id)
            logger.info(cmd)   
            proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()


def single_mode(ip_addr,project_id):

    cmd =  xpython + ' ' + 'checkdetail.py'  + "  " + ip_addr+ "  " +project_id
    logger.info(cmd)   
    proc = Popen(cmd.split(),shell=False,cwd=cpath) 


    cmd= cpath+'masscan.py '
    cmd =  xpython + ' ' + cmd  + '  ' + "  " + ip_addr+ "  " +project_id
    logger.info(cmd)   
    proc = Popen(cmd.split(),shell=False,cwd=cpath) 


def usage():
    print """
    checktask.py ip_addr    project_id 
    """      
 

if __name__ == '__main__':
    if len(sys.argv) ==  3:
        ip_addr = sys.argv[1]
        project_id =  sys.argv[2]
        single_mode(ip_addr,project_id )

    elif len(sys.argv) ==  1:
        main()
    else:
        usage()
        


