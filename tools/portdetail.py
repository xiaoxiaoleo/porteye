# encoding:utf-8
# copy by evileo

import os
from libs.utils import postHttp, getJsonHttp, list_int2str
from common.tool import logger
from common.config import cpath, xpython, master_server

def run_fnascan(project_id, ip_addr, port_list):
    #####run fnascan
    default_need_scan = ['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
    for  p in port_list:
        if p not in default_need_scan:
            default_need_scan.append(p)

    logger.info("FNASCAN PORT : "+str(default_need_scan))
    need_scan_port = ','.join(list_int2str(default_need_scan))
    jsonfilename = ip_addr + '.html'
    os.chdir(cpath + '/tools/fnascan/')
    cmd = xpython + ' ' + cpath + '/tools/fnascan/fnascan.py  -h ' + ip_addr + ' -p ' + need_scan_port
    logger.info(cmd)  
    os.system(cmd)

    try:
        result_file = open('./'+jsonfilename)
        postdata = result_file.read()
        data = {'domain' : ip_addr, 'project_id' : project_id, 'data' : postdata}
        result_file.close()
        os.remove('./'+jsonfilename)
    except Exception, e:
        logger.error(e)

    serverurl = 'http://'+master_server+'/web/upload_fnascan_result'
    logger.info(serverurl)  
    postHttp(serverurl, data)


# def run_wyportmap(project_id, ip_addr, port_list):
#     logger.info("PORT FROM OpenPort : "+str(port_list))
#     default_need_scan = ['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
#     for  p in port_list:
#         if p not in default_need_scan:
#             default_need_scan.append(p)
#
#     ###run wyport map
#     need_scan_port = ','.join(default_need_scan)
#     logger.info("PORT WILL WYPORTMAP SCAN : "+need_scan_port)
#     try:
#         cmd =  "sudo " +  xpython + ' ' +'   '+ 'tools/wyportmap/wyportmap.py'+'  ' + ip_addr + '  ' +need_scan_port + '  ' +  str(project_id)
#         logger.info(cmd)
#         proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()
#     except Exception,e:
#         logger.error(e)
#         passdef run_wyportmap(project_id, ip_addr, port_list):
#     logger.info("PORT FROM OpenPort : "+str(port_list))
#     default_need_scan = ['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
#     for  p in port_list:
#         if p not in default_need_scan:
#             default_need_scan.append(p)
#
#     ###run wyport map
#     need_scan_port = ','.join(default_need_scan)
#     logger.info("PORT WILL WYPORTMAP SCAN : "+need_scan_port)
#     try:
#         cmd =  "sudo " +  xpython + ' ' +'   '+ 'tools/wyportmap/wyportmap.py'+'  ' + ip_addr + '  ' +need_scan_port + '  ' +  str(project_id)
#         logger.info(cmd)
#         proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()
#     except Exception,e:
#         logger.error(e)
#         passdef run_wyportmap(project_id, ip_addr, port_list):
#     logger.info("PORT FROM OpenPort : "+str(port_list))
#     default_need_scan = ['21', '22', '23', '24', '25', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '110', '143', '443', '513', '873', '1080', '1433', '1521', '1158', '3306', '3307', '3308', '3389', '3690', '5900', '6379', '7001', '8000-8090', '9000', '9418', '27017', '27018', '27019', '50060', '111', '11211', '2049', '53', '139', '389', '445', '465', '993', '995', '1723', '4440', '5432', '5800', '8000', '8001', '8080', '8081', '8888', '9200', '9300', '9080', '9999']
#     for  p in port_list:
#         if p not in default_need_scan:
#             default_need_scan.append(p)
#
#     ###run wyport map
#     need_scan_port = ','.join(default_need_scan)
#     logger.info("PORT WILL WYPORTMAP SCAN : "+need_scan_port)
#     try:
#         cmd =  "sudo " +  xpython + ' ' +'   '+ 'tools/wyportmap/wyportmap.py'+'  ' + ip_addr + '  ' +need_scan_port + '  ' +  str(project_id)
#         logger.info(cmd)
#         proc = Popen(cmd.split(),shell=False,cwd=cpath).wait()
#     except Exception,e:
#         logger.error(e)
#         pass


#
# def scan_single_ip(ip_addr,project_id = 0):
#     if not project_id:
#         ret = getJsonHttp('http://'+master_server+'/ip_address_to_project_id?ip_addr=%s' % ip_addr)
#         project_id = ret['data']
#
#     ret = getJsonHttp('http://'+master_server+'/list_all_open_port?ip_addr=%s' % ip_addr)
#     port_list = ret['data']
#
#     #port_list  = list_str2int(port_list)
#     run_wyportmap(project_id = project_id,ip_addr = ip_addr ,port_list =  port_list)
#     #get wyportmap open portlist,then push to /web/uploadopenport
#
#     # 判断是否是new port
#     # _open_port = []
#     # try:
#     #     newest_insert_time = ResultPorts.objects.filter(address = ip_addr).values_list('inserted',flat=True).order_by('-inserted')[0]
#     #     _open_port = ResultPorts.objects.filter(inserted = newest_insert_time).values_list('port',flat=True).distinct()
#     # except Exception,e:
#     #     logger.error(e)
#     #     pass
#     # _open_port = list_int2str(_open_port)
#     # _all_ports  = '-'.join(_open_port)
#     # data = {'domain':ip_addr,'project_id':project_id,'data': _all_ports}
#     # logger.info(data)
#     # serverurl = 'http://'+master_server+'/uploadopenport'
#     # postHttp(serverurl ,data)
#
#     run_fnascan(project_id = project_id,ip_addr = ip_addr,_open_port = _open_port)
#
# def scan_db_ip():
#     ret = getJsonHttp('http://'+master_server+'/list_all_ip')
#     all_ip = list(ret['data'])
#     for ip_addr in all_ip:
#         scan_single_ip(ip_addr = ip_addr)


def test_uploadfnascan():
    run_fnascan(1,'x.x.x.x', ['22', '80', '443', '1883', '18301'])

