#!/usr/bin/env python
# encoding:utf-8

import sys
import time
from optparse import OptionParser
from subprocess import Popen
from common.config import master_server
from common.tool import logger
from libs.utils import getJsonHttp
from tools.portalive import portalive
from tools.portdetail import  run_fnascan
from tools.portalive import test as portalive_test
from tools.hostalive import hostalive



def host_alive():
    hostalive(ip_addr, project_id)

def scan_db_ip_range():
    pass

def scan_db_ip():
    pass

def scan_db_project():
    pass

def scan_sigle_ip(ip_addr, project_id):
    
    portalive(ip_addr, project_id)

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

    parser = OptionParser()

    parser.add_option("-f", "--file", action="store", dest="filename", default="foo.txt")
    parser.add_option("-v", action="store_true", dest="verbose", default=True)
    parser.add_option("-t", action="store", dest="test_fun", default=True)
    parser.add_option("-s", "--scan", action="store", dest="scan", default="")
    parser.add_option("-p", "--project", action="store", dest="project_id", default="")
    parser.add_option("-i", "--ip", action="store", dest="ip_addr", default="")

    (option, arges) = parser.parse_args()

    print (option, arges)

    if option.scan == 'host_alive':
        hostalive(option.ip_addr, option.project_id)
    if option.scan == 'port_alive':
        portalive(option.ip_addr, option.project_id)
    if option.scan == 'port_alive_detail':
        scan_sigle_ip(option.ip_addr, option.project_id)

    if option.test_fun == '123':
        test()


