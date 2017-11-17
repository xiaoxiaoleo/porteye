# encoding:utf-8
# code by evileo

import json
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from  web.models import  OpenPort,PortAliveProject,FnascanResult,ResultPorts,ResultIp,IpRemarks,AliveHost
from django.views.decorators.csrf import csrf_exempt
from common.tool import  logger
import datetime

def http_return(data):
    if not data['data'] :
        return HttpResponse(json.dumps({'result':True,'data':False}))
    return HttpResponse(json.dumps(data))

def list_alive_host(request):
    project_id = request.GET.get('project_id', '')
    if project_id == 'all':
        ip_list = list(AliveHost.objects.values_list('ip_addr',flat=True).all())
        return http_return({'result': True, 'data': ip_list})
    if project_id:
        ip_list = list(AliveHost.objects.values_list('ip_addr',flat=True).filter(project_id = project_id))
        return http_return({'result': True, 'data': ip_list})

def list_ip_range(request):
    project_id = request.GET.get('project_id', '')
    # if project_id == 'all':
    #     ip_list = list(AliveHost.objects.values_list('ip_addr',flat=True).all())
    #     return http_return({'result': True, 'data': ip_list})
    if project_id:
        ip_list = list(AliveHost.objects.values_list('ip_addr',flat=True).filter(project_id = project_id))
        return http_return({'result': True, 'data': ip_list})


def list_all_ip(request):
    allip = list(OpenPort.objects.values_list('ip',flat=True).order_by('last_checkdetail_time').distinct())
    return http_return({'result':True,'data':allip}) 

def list_all_open_port(request):
    ip_addr = request.GET.get('ip_addr', '')
    port_list = list(OpenPort.objects.values_list('port', flat = True).filter(ip = ip_addr, port_status = 1))
    return http_return({'result':True,'data':port_list})

def list_all_ip_range(request):
    all_ip_range = PortAliveProject.objects.all()
    return http_return({'result':True,'data':all_ip_range}) 

def ip_address_to_project_id(request):
    ip_addr = request.GET.get('ip_addr', '')
    project_id = OpenPort.objects.values_list('project_id',flat=True).filter(ip=ip_addr).distinct()[0]
    return http_return({'result':True,'data':project_id})


@csrf_exempt
def upload_alive_host(request):
    if request.method == 'POST':
        req_dic = json.loads(json.dumps(request.POST))
        project_id = int(req_dic['project_id'])
        new_ip_list = req_dic['data'].split('-')

        #old_ip_list = AliveHost.objects.values_list('port', flat = True).filter(project_id = project_id, is_up = 1)
        AliveHost.objects.filter(project_id = project_id).delete()

        for ip in new_ip_list:
            _tmp_obj = AliveHost(project_id = project_id, ip_addr = ip)
            _tmp_obj.save()

        return HttpResponse(json.dumps({'result': True, 'info': ''}))


@csrf_exempt
def upload_open_port(request):
    if request.method == 'POST':
        req_dic = json.loads(json.dumps(request.POST))
        projectid = int(req_dic['project_id'])
        new_port_list =  req_dic['data'].split('-')
        ip_addr = str(req_dic['ip_addr'])
        
        old_port_list = OpenPort.objects.values_list('port', flat=True).filter(ip=ip_addr, port_status=1)
        logger.info('RECEIVED IP: '  + str(ip_addr) )
        logger.info('old_port_list'  + str(old_port_list) )
        logger.info('new_port_list'  + str(new_port_list) )

        #new port!
        True_open_port_list = set(new_port_list) - set(old_port_list) 
        True_close_port_list = set(old_port_list) - set(new_port_list) 

        for i in list(True_open_port_list):
            _tmp_query =  OpenPort.objects.filter(ip = ip_addr, port = i)
            if len(_tmp_query) < 1:
                _tmp_obj = OpenPort(project_id=projectid,ip=ip, port = i, insert_time = datetime.datetime.now(), findby = 'masscan', update_time = datetime.datetime.now())
                _tmp_obj.save()
            if len(_tmp_query) == 1:
                _tmp_obj = OpenPort.objects.get(ip = ip_addr, port = i)
                _tmp_obj.update_time  =  datetime.datetime.now()
                _tmp_obj.port_status = 1
                _tmp_obj.save()
    
        for i in list(True_close_port_list):
            _tmp_obj = OpenPort.objects.get(ip = ip_addr, port = i)
            _tmp_obj.update_time  =  datetime.datetime.now()
            _tmp_obj.port_status = 0
            _tmp_obj.save()

        OpenPort.objects.filter(ip = ip_addr).update(last_checkdetail_time =  datetime.datetime.now())

        return HttpResponse(json.dumps({'result':True,'info':''}))


@csrf_exempt
def upload_fnascan_result(request):
    if request.method == 'POST':
        req_dic = json.loads(json.dumps(request.POST))
        projectid = int(req_dic['project_id'])

        if req_dic['data'] == '{}':
            return HttpResponse(json.dumps({'result': False, 'data': 'i receive noting!'}))

        data = req_dic['data'].split('\n____\n')
        # if len(data) >2:
        #     insert_fnascametadata(projectid,data[0],data[1],data[2])

        port_service_list = eval(data[0])
        port_service_list = port_service_list[0]['submenu'][0]['submenu']
        service_detail_list = eval(data[1])

        port_list = []
        i_ip = ''
        for i in port_service_list:
            print i
            i_ip, i_port = i['url'].split(':')
            logger.info(i_ip)
            port_list.append(i_port)
            i_service = i['name']
            i_title = ''
            i_service_detail = ''
            # print i['url']
            try:
                i_service_detail = service_detail_list[i['url'].strip()]
            except Exception, e:
                logger.error(e)
                pass
            if len(i_service.split('web ||')) == 2:
                i_title = i_service.split('web ||')[1]
                i_service = i_service.split('web ||')[0] + 'web'

            insert_fnascanresult(i_ip, i_port, i_service, projectid, i_service_detail, i_title)

        update_fnascan_port_status(i_ip, port_list)

        return HttpResponse(json.dumps({'result': True, 'info': ''}))


def update_fnascan_port_status(ip, new_port_list):
    old_port_list = FnascanResult.objects.values_list('port', flat=True).filter(ip=ip, port_status=1)
    logger.info('RECEIVED IP: ' + str(ip))
    logger.info('old_port_list' + str(old_port_list))
    logger.info('new_port_list' + str(new_port_list))

    # new port!
    True_open_port_list = set(new_port_list) - set(old_port_list)
    True_close_port_list = set(old_port_list) - set(new_port_list)

    for i in list(True_open_port_list):
        _tmp_query = FnascanResult.objects.filter(ip=ip, port=i)

        if len(_tmp_query) == 1:
            _tmp_obj = OpenPort.objects.get(ip=ip, port=i)
            _tmp_obj.update_time = datetime.datetime.now()
            _tmp_obj.port_status = 1
            _tmp_obj.save()

    for i in list(True_close_port_list):
        _tmp_obj = FnascanResult.objects.get(ip=ip, port=i)
        _tmp_obj.update_time = datetime.datetime.now()
        _tmp_obj.port_status = 0
        _tmp_obj.save()


# new port find!
def insert_fnascanresult(i_ip, i_port, i_service, projectid, i_service_detail, i_title):
    try:
        i_service = i_service.split(" ")[1].replace("(default)", "")
    except Exception, e:
        logger.error(e)
        pass
    # current_time = int(time.time())
    # old list
    _tmp_list = FnascanResult.objects.filter(project_id=projectid, ip=i_ip, port=i_port)
    # if new port !
    if len(_tmp_list) == 0:
        _fnascan_result = FnascanResult(project_id=projectid, ip=i_ip, port=i_port, service_name=i_service,
                                        service_detail=i_service_detail, web_title=i_title)
        _fnascan_result.insert_time = datetime.datetime.now()

        _fnascan_result.last_check_time = datetime.datetime.now()
        _fnascan_result.save()

    # if not new port   !
    elif len(_tmp_list) == 1:
        _fnascan_result = FnascanResult.objects.get(project_id=projectid, ip=i_ip, port=i_port)
        _fnascan_result.service_name = i_service
        _fnascan_result.i_service_detail = i_service_detail
        _fnascan_result.i_title = i_title

        _fnascan_result.last_check_time = datetime.datetime.now()
        _fnascan_result.save()
