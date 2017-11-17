# encoding:utf-8
# copy by evileo

import time
from subprocess import Popen
import xml.dom.minidom
from common.config import  nmap_dir, master_server
from common.tool import logger
from libs.utils import postHttp



def hostalive(ip_addr, project_id):
    try:
        #http://www.lijiejie.com/nmap-fast-scan-large-networks/
        cmd =  "sudo " + nmap_dir +"/nmap -v -sn -PE -n --min-hostgroup 1024 --min-parallelism 1024 -oX /tmp/nmap_output.xml "  + ip_addr
        logger.info(cmd)
        Popen(cmd.split(),shell=False, cwd=nmap_dir).wait()


        fname = "/tmp/nmap_output.xml"
        try:
            doc = xml.dom.minidom.parse(fname)
        except IOError:
            print "%s: error: file  doesn't exist\n" % ( fname)

        except xml.parsers.expat.ExpatError:
            print "%s: error: file  doesn't seem to be XML\n" % ( fname)

        alive_host_list = []
        for host in doc.getElementsByTagName("host"):
            try:
                address = host.getElementsByTagName("address")[0]
                ip = address.getAttribute("addr")
            except:
                # move to the next host since the IP is our primary key
                continue
            try:
                status = host.getElementsByTagName("status")[0]
                state = status.getAttribute("state")
            except:
                state = ""

            if state == 'up':
                alive_host_list.append(ip)


        _all_ip = '-'.join(alive_host_list)
        logger.info(_all_ip)
        serverurl = 'http://'+ master_server+'/web/upload_alive_host'
        #{u'project_id':  11 , u'project_id': [u'271'], u'data': [u'33147-22147-63886-30147-6379-21147']}
        logger.info(serverurl)

        data = {'project_id':project_id, 'data': _all_ip}
        logger.info(data)
        postHttp(serverurl, data)
        time.sleep(1)

    except Exception,e:
        logger.error(e)
        return
