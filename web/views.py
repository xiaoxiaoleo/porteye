# Create your views here.
# encoding:utf-8

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt 
import json
import datetime
from  web.models import  PortAliveProject,OpenPort,PortAliveProject,FnascanResult,ResultPorts,ResultIp,IpRemarks
from common.tool import  logger
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login/")
def index(request):
    return render_to_response('portmonitor_index.html', {}, context_instance=RequestContext(request))


@login_required(login_url="/login/")
def getproject(request):
    res = []
    data = PortAliveProject.objects.filter(ports_check =1)
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
def all_project(request):
    
    obj_list = PortAliveProject.objects.all().order_by('id')
 
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


 

def ip_scan(request):
    pass