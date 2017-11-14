
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from  web.models import  port_alive_project,OpenPort,port_monitor,FnascanResult,ResultPorts,ResultIp,IpRemarks

def http_return(data):
    if not data['data'] :
        return HttpResponse(json.dumps({'result':True,'data':False}))
    return HttpResponse(data)

def list_all_ip(request):
    allip =OpenPort.objects.values_list('ip',flat=True).order_by('last_checkdetail_time').distinct()
    return http_return({'result':True,'data':allip}) 

def list_all_ip_range(request):
    all_ip_range = port_monitor.objects.all()
    return http_return({'result':True,'data':all_ip_range}) 

