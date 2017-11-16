# encoding:utf-8
# code by evileo

import sys
from subprocess import Popen
import xmltodict
import datetime,time
from libs.utils import postHttp, sort_masscan
from common.tool import  logger
from common.config import master_server,masscan_dir

def portalive(ip_addr,project_id):
    try:
        cmd =  "sudo " + masscan_dir +"/masscan --ports 1-65535  " + ip_addr +" --max-rate 3000  --source-port 60000 -oX /tmp/scanoutput.xml" 
        logger.info(cmd)
        Popen(cmd.split(),shell=False, cwd=masscan_dir).wait()

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
            serverurl = 'http://'+master_server+'/web/upload_open_port'
            #{u'domain': [u'172.32.1.100'], u'project_id': [u'271'], u'data': [u'33147-22147-63886-30147-6379-21147']}
            logger.info(serverurl)  

            data = {'ip_addr':_ip,'project_id':project_id,'data': _all_ports}
            logger.info(data)
            postHttp(serverurl ,data)
            time.sleep(1)

    except Exception,e:
        logger.error(e)
        return


def test():
    #cmd = "sudo /home/leo/Desktop/porteye/masscan/bin/masscan --ports 1-65535  172.32.1.147 --max-rate 3000  --source-port 60000 -oX /tmp/scanoutput.xml"
    # cmd ='whoami'
    # #logger.info(cmd)
    # print cmd
    # proc = Popen(cmd.split(),shell=False,cwd=masscan_dir).wait()
    serverurl = 'http://'+master_server+'/web/upload_open_port'
    #{u'domain': [u'172.32.1.100'], u'project_id': [u'271'], u'data': [u'33147-22147-63886-30147-6379-21147']}
    logger.info(serverurl)
    data = {'ip_addr':'127.0.0.1','project_id':333,'data': '49666-9421-15485-445-902-62806-65412-65325-49665-49182-65453-9088-9088-49668-49669-912-23401-135-49664-65452-49667'}
    logger.info(data)
    postHttp(serverurl ,data)

