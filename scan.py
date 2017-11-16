#!/usr/bin/env python
# encoding:utf-8

import sys
import time
from subprocess import Popen
from common.config import cpath, xpython, master_server
from common.tool import logger
from libs.utils import getJsonHttp
from tools.portalive import portalive
from tools.portdetail import  run_fnascan
from tools.portalive import test as portalive_test

def scan_db_ip_range():
    pass

def scan_db_ip():
    pass

def scan_db_project():
    pass



def scan_sigle_ip(ip_addr,project_id):
    
    portalive(ip_addr,project_id)

    ret = getJsonHttp('http://'+master_server+'/web/list_all_open_port?ip_addr=%s' % ip_addr)
    port_list = ret['data']

    run_fnascan(project_id, ip_addr, port_list)



def test():
    portalive_test()
    
def usage():
    print """
    scan.py ip_addr    project_id 
    """

if __name__ == '__main__':
    if len(sys.argv) ==  3:
        ip_addr = sys.argv[1]
        project_id =  sys.argv[2]
        scan_sigle_ip(ip_addr,project_id )
    elif len(sys.argv) ==  1:
        scan_db_ip()
    elif len(sys.argv) ==  2:
        test()
    else:
        usage()
        


