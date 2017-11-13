#!/usr/bin/env python
# encoding:utf-8

import sys
import time
from subprocess import Popen
from common.config import cpath,xpython
from common.tool import logger

def scan_db_ip():
    while(1):

        time.sleep(1)

        alltask =port_monitor.objects.all().order_by('id')
        task_length = len(alltask)
        
        for i in range(0,task_length):
            curobj = alltask[i]

            cmd =  xpython + ' ' + 'checkdetail.py'
            logger.info(cmd)   
            Popen(cmd.split(),shell=False,cwd=cpath).wait()

            cmd= cpath+'masscan.py '
            cmd =  xpython + ' ' + cmd  + '  '+  curobj.ip_range +'  ' +  str(curobj.id)
            logger.info(cmd)   
            Popen(cmd.split(),shell=False,cwd=cpath).wait()


def scan_sigle_ip(ip_addr,project_id):

    cmd =  xpython + ' ' + 'tools/portdetail.py'  + "  " + ip_addr+ "  " +project_id
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
        scan_sigle_ip(ip_addr,project_id )
    elif len(sys.argv) ==  1:
        scan_db_ip()
    else:
        usage()
        


