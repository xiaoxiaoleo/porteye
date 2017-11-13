# Create your views here.
# encoding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt 
import json
# from setting.models import server_setting
 
from  portmonitor.models import  port_alive_project,OpenPort,port_monitor,FnascanResult,ResultPorts,ResultIp,IpRemarks
from libs.mylogger import mylogger
logger = mylogger('portmonitor.views.py')
from libs.utils import list_str2int,list_int2str

import datetime 
def index(request):
     
    return render_to_response('index_portmonitor.html' ,{},context_instance=RequestContext(request))




@login_required(login_url="/login/")
def getproject(request):
    res = []
    data = port_alive_project.objects.filter(ports_check =1)
    for i in data:
        # _t = checktask.objects.filter(project_id=i.id) 
        lastcheck_time = ''
        lastcheck_time = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(float(lastcheck_time)))
        res.append({'id':i.id,'name':i.name,'domain':i.domain,'port':i.port,'check_frequency':i.check_frequency,
                    'notify_rule_id':1, 'create_time':time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(float(i.create_time))),
                    'lastcheck_time':lastcheck_time,
                    'heartbleed_check':i.heartbleed_check,'ccs_check':i.ccs_check,
                     'hsts_check':i.hsts_check, 'status':i.status,'statusinfo':i.statusinfo,'notify_rule_name':'mail'
                    }) 
 
    return HttpResponse(json.dumps({'result':True,'data':res})) 

def get_os(ip_addr):
    try:
        ip_os = ResultIp.objects.values_list('os',flat=True).filter(address= ip_addr).order_by('-inserted')[0]
    except:
        ip_os = 'unknow'
    return ip_os

def get_fnascan_lastchecktime(ip_addr):
    try:
        ip_os = ResultIp.objects.values_list('os',flat=True).filter(address= ip_addr).order_by('-inserted')[0]
    except:
        ip_os = 'unknow'
    return ip_os

def get_masscan_lastchecktime(ip_addr):
    try:
        ip_os = ResultIp.objects.values_list('os',flat=True).filter(address= ip_addr).order_by('-inserted')[0]
    except:
        ip_os = 'unknow'
    return ip_os


@login_required(login_url="/login/")
def openport(request):
    project_id = request.GET.get('project_id', '')
    #_ip_list =  project.objects.values_list('domain',flat=True).filter(ports_check=1)
    #for _ip in _ip_list:
    if project_id:
        ip_list =  OpenPort.objects.values_list('ip',flat=True).filter(port_status=1,project_id = project_id).distinct().order_by('ip')
        #print ip_list
        obj_alldic = {}

        os_alldic = {}

        port_count = 0
        for _ip  in ip_list:
            os_alldic[_ip]  =  get_os(_ip)


            _ip_ports = []
            _obj_all = OpenPort.objects.filter(ip=_ip,port_status=1).distinct() 
            for _p in _obj_all:
                _ip_ports.append(_p.port)

            if len(_ip_ports) > 0:
                obj_alldic[_ip] = _ip_ports

            port_count = port_count + len(_ip_ports)
     
        return render(
            request,
            'portmonitor_openport.html',
            context_instance = RequestContext(request,
            {
            'obj_all': obj_alldic,
            'server_count':len(obj_alldic),
            'port_count':port_count,
            'os_alldic':os_alldic
            })
        )

def singleopenport(request):
    ip_addr = request.GET.get('ip_addr', '')

 
    _ip_ports = []
    _obj_all = OpenPort.objects.filter(ip=str(ip_addr.strip()),port_status=1).distinct() 
    for _p in _obj_all:
        _ip_ports.append(_p.port)

 
    port_count =  len(_ip_ports)
 
    return render(
        request,
        'portmonitor_singleopenport.html',
        context_instance = RequestContext(request,
        {
        'obj_all': _obj_all, 
        'port_count':port_count,
        'ip_addr':ip_addr
        })
    )
 
@login_required(login_url="/login/") 
def ipdetail(request):
    error_message = ''
    ip_addr = request.GET.get('ip_addr', '')
    ip_addr = ip_addr.strip()
    if ip_addr:
        insert_time_list = ResultPorts.objects.values_list('inserted',flat=True).filter(address=ip_addr).distinct().order_by('-inserted')
        #print insert_time_list[0]
        if len(insert_time_list) > 0:
            last1_obj =  ResultPorts.objects.filter(address=ip_addr,inserted = insert_time_list[0]).order_by('port')
            
            fnascan_objs = FnascanResult.objects.filter(ip=ip_addr)

            ipremark = IpRemarks.objects.filter(ip_addr=ip_addr)


            return render(
                request,
                'portmonitor_ipdetail.html',
                context_instance = RequestContext(request,
                {
                'obj_all': last1_obj, 
                'port_count':len(last1_obj),
                'ip_addr':ip_addr,
                'fnascan_objs' :fnascan_objs,
                'os_info':get_os(ip_addr),
                'ipremark':ipremark
                })
            )
        else:
            error_message = 'wyportmap resultport return nothing'
    


    return render(

        request,
        'error.html',
        context_instance = RequestContext(request,
        {
        'error_message':error_message,
        })
    )
 

@login_required(login_url="/login/")
def main_project(request):
    obj_list = port_monitor.objects.all().order_by('id')
 
    return render(
        request,
        'portmonitor_main_project.html',
        context_instance = RequestContext(request,
        {
        
        'obj_list':obj_list,
        'server_count':111111111,
        'port_count':111
        })
    )
 

@login_required(login_url="/login/")
def alivehost(request):
    project_id = request.GET.get('project_id', '')
    if  project_id:
        ip_list =  OpenPort.objects.values_list('ip',flat=True).filter(project_id=str(project_id),port_status=1).distinct()
 
        return render(
            request,
            'portmonitor_alivehost.html',
            context_instance = RequestContext(request,
            {
            
            'project_id':project_id,
            'ip_list':ip_list,
            'ip_count':len(ip_list),
            })
        )
    

 


    else:
        error_message = ''
        return render(
            request,
            'error.html',
            context_instance = RequestContext(request,
            {
            'error_message':error_message,
            })
        )



@csrf_exempt
def uploadopenport(request):
    rawjson = json.loads(json.dumps(request.POST))
    projectid = int(rawjson['project_id'])
    new_port_list =  rawjson['data'].split('-')
    ip = str(rawjson['domain'])  
    

    old_port_list = OpenPort.objects.values_list('port',flat=True).filter(ip=ip,port_status=1)
    logger.info('RECEIVED IP: '  + str(ip) )
    logger.info('old_port_list'  + str(old_port_list) )
    logger.info('new_port_list'  + str(new_port_list) )

    #new port!
    True_open_port_list = set(new_port_list) - set(old_port_list) 
    True_close_port_list = set(old_port_list) - set(new_port_list) 

    for i in list(True_open_port_list):
        _tmp_query =  OpenPort.objects.filter(ip=ip ,port = i)
        if len(_tmp_query) < 1:
            _tmp_obj = OpenPort(project_id=projectid,ip=ip ,port = i,insert_time =  datetime.datetime.now(),findby = 'masscan',update_time  =  datetime.datetime.now())
            _tmp_obj.save()
        if len(_tmp_query) == 1:
            _tmp_obj = OpenPort.objects.get(ip=ip ,port = i)
            _tmp_obj.update_time  =  datetime.datetime.now()
            _tmp_obj.port_status = 1
            _tmp_obj.save()
 
    for i in list(True_close_port_list):
        _tmp_obj = OpenPort.objects.get(ip=ip ,port = i)
        _tmp_obj.update_time  =  datetime.datetime.now()
        _tmp_obj.port_status = 0
        _tmp_obj.save()

    OpenPort.objects.filter(ip=ip).update(last_checkdetail_time =   datetime.datetime.now())

    return HttpResponse(json.dumps({'result':True,'info':''})) 

@csrf_exempt
def uploadfnascanresult(request):
    rawjson = json.loads(json.dumps(request.POST))
    projectid = int(rawjson['project_id'])
    #print 10000*'a'
    #print rawjson['data']
    if  rawjson['data']  == '{}':
        return HttpResponse(json.dumps({'result':False,'data':'i receive noting!'}))

    data=rawjson['data'].split('\n____\n')
    # if len(data) >2:
    #     insert_fnascametadata(projectid,data[0],data[1],data[2])


    port_service_list =  eval(data[0])
    port_service_list =  port_service_list[0]['submenu'][0]['submenu']
    service_detail_list = eval(data[1])
 

    port_list =[]
    i_ip = ''
    for  i in port_service_list:
        print i
        i_ip,i_port = i['url'].split(':')
        logger.info(i_ip)
        port_list.append(i_port)
        i_service = i['name'] 
        i_title = ''
        i_service_detail = ''
        #print i['url']
        try:
            i_service_detail = service_detail_list[i['url'].strip()]
        except Exception,e:
            logger.error(e)
            pass
        if len(i_service.split('web ||') )== 2:

            i_title = i_service.split('web ||')[1]
            i_service = i_service.split('web ||')[0]+'web'

        insert_fnascanresult(i_ip,i_port,i_service,projectid,i_service_detail,i_title)

    update_fnascan_port_status(i_ip,port_list)


    return HttpResponse(json.dumps({'result':True,'info':''})) 

 
def update_fnascan_port_status(ip,new_port_list):
    old_port_list = FnascanResult.objects.values_list('port',flat=True).filter(ip=ip,port_status=1)
    logger.info('RECEIVED IP: '  + str(ip) )
    logger.info('old_port_list'  + str(old_port_list) )
    logger.info('new_port_list'  + str(new_port_list) )

    #new port!
    True_open_port_list = set(new_port_list) - set(old_port_list) 
    True_close_port_list = set(old_port_list) - set(new_port_list) 

    for i in list(True_open_port_list):
        _tmp_query =  FnascanResult.objects.filter(ip=ip ,port = i)
 
        if len(_tmp_query) == 1:
            _tmp_obj = OpenPort.objects.get(ip=ip ,port = i)
            _tmp_obj.update_time  =  datetime.datetime.now()
            _tmp_obj.port_status = 1
            _tmp_obj.save()
 
    for i in list(True_close_port_list):
        _tmp_obj = FnascanResult.objects.get(ip=ip ,port = i)
        _tmp_obj.update_time  =  datetime.datetime.now()
        _tmp_obj.port_status = 0
        _tmp_obj.save()

#new port find!
def insert_fnascanresult(i_ip,i_port,i_service,projectid,i_service_detail,i_title):
    try:
        i_service =  i_service.split(" ")[1].replace("(default)","")
    except Exception,e:
        logger.error(e)
        pass
    #current_time = int(time.time())
    # old list 
    _tmp_list = FnascanResult.objects.filter(project_id = projectid,ip = i_ip,port = i_port)
    #if new port !
    if len(_tmp_list) == 0:
        _fnascan_result = FnascanResult(project_id = projectid, ip = i_ip,port = i_port, service_name = i_service, service_detail=i_service_detail,web_title = i_title)
        _fnascan_result.insert_time =  datetime.datetime.now()

        _fnascan_result.last_check_time = datetime.datetime.now()
        _fnascan_result.save()
         
    # if not new port   !   
    elif  len(_tmp_list) == 1:
        _fnascan_result = FnascanResult.objects.get(project_id = projectid, ip = i_ip,port = i_port)
        _fnascan_result.service_name = i_service
        _fnascan_result.i_service_detail = i_service_detail
        _fnascan_result.i_title  = i_title

        _fnascan_result.last_check_time = datetime.datetime.now()
        _fnascan_result.save()

 

def ip_scan(request):
    pass