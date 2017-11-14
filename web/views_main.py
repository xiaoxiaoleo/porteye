# encoding:utf-8
# code by evileo
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt 
import json,os,datetime,time
from web.models import  alertlog, project
import urllib
from common.tool import logger
from hconfig import cpath,xpython,distribute_server_list

@login_required(login_url="/login/")
def index(request):
    return render_to_response('index.html' ,{},context_instance=RequestContext(request))

def certs(request):
    return render_to_response('cert.html' ,{},context_instance=RequestContext(request))

def certdetail(request):
    return render_to_response('certdetail.html' ,{'id':request.GET['id']},context_instance=RequestContext(request))

@login_required(login_url="/login/")
def create(request):
    return render_to_response('create.html' ,{},context_instance=RequestContext(request))

@login_required(login_url="/login/")
def create_portmonitor(request):
    return render_to_response('portmonitor_create.html', {}, context_instance=RequestContext(request))

@login_required(login_url="/login/")
def report(request):
    userid=1  
    
    #pid = request.GET['id']
    pid = request.GET.get('id', '')
    ip = request.GET.get('ip', '')


    if ip:
        data = port_alive_project.objects.filter(domain = ip)
    if pid:
        data = ssl_project.objects.filter(user_id=userid,id=pid)

    if len(data) ==0:
        return HttpResponse(json.dumps({'result':False,'data':'project id error'}))
    p =  data[0]
    if p.ports_check == 1:
        return render_to_response('report_portmonitor.html' ,{'id':pid,'ip':ip},context_instance=RequestContext(request))
    else:
        return render_to_response('report.html' ,{'id':pid,'ip':ip},context_instance=RequestContext(request))
 
 
  
@login_required(login_url="/login/")
@csrf_exempt
def createproject(request):
        userid=1  
        data = json.loads(request.body)
        extchk =  data['extern_check'].split(';')
        chk={'ccs':False,'hsts':False,'heartbleed':False,'poodle':False,'ports_check':False}
 
        for i in extchk: 
            if len(i)>1:
                if not chk.has_key(i):
                    return HttpResponse(json.dumps({'result':False,'info':'extern_check data invalid'})) 
                
                chk[i] = True
        #TODO check args
        
        domains = data['domain'].split(';')
        name = data['name']
        frequency = data['frequency']
        notify_id = 1
        port = int(data['port'])
        

        for d in domains:
            exdomain=project.objects.filter(user_id=userid,domain=d,ports_check=0)
            if len(exdomain)>0:
                return HttpResponse(json.dumps({'result':False,'info':'domain '+d+' existed'})) 
        if  port ==0:
            for d in domains:
                exdomain=project.objects.filter(user_id=userid,domain=d,ports_check=1)
                if len(exdomain)>0:
                    return HttpResponse(json.dumps({'result':False,'info':'domain '+d+' existed'})) 


        for d in domains:
            tmp = project(user_id=userid,name=name,port=port,domain=d,
                          check_frequency=frequency,
                          notify_rule_id=notify_id,
                          create_time=time.time(),
                          heartbleed_check=chk['heartbleed'],
                          ccs_check=chk['ccs'],
                          hsts_check=chk['hsts'],
                          poodle_check=chk['poodle'],
                          ports_check=chk['ports_check'],
                          status=0)
            tmp.save();
            #print tmp.id
            cmd =  xpython+' '+cpath+'/uploadproject.py -i '+str(tmp.id) +'&'
            logger.info(cmd)
            os.system(cmd)
            logger.info(cmd)

        return HttpResponse(json.dumps({'result':True,'info':''})) 

@login_required(login_url="/login/")
def delproject(request):
    userid=1  
    try: 
        pid = request.GET['id']
        pjt=project.objects.filter(user_id=userid,id=pid)
        
        if len(pjt) == 0:
            return HttpResponse(json.dumps({'result':False,'info':u'无法删除此项目'})) 
        

        if get_monitor_type(pid) == 'ssl_check':
            chkres=checkresult.objects.filter(project_id=pid)
            
 
            for clientip in distribute_server_list: 
                f = urllib.urlopen('http://'+clientip+'/sslcheck/delchecktask?id='+str(pid))
                
                print f.read()
            
            for i in chkres:
                i.delete()
 
        if get_monitor_type(pid) == 'ports_check':
            chkres=  FnascanResult.objects.filter(project_id=pid)
            chkres_metadata=  FnascanMetadata.objects.filter(project_id=pid)
 
            for clientip in distribute_server_list: 
                f = urllib.urlopen('http://'+clientip+'/portscheck/delchecktask?id='+str(pid))
                print f.read()
            
            for i in chkres:
                i.delete()

            for i in chkres_metadata:
                i.delete()
        pjt.delete()

        return HttpResponse(json.dumps({'result':True,'info':'ok'}))  
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'result':False,'info':'delproject'+str(e)})) 

 


"""
newport
reopen
nowclose
close
open
"""
def insert_warning_log(project_id='',i_ip='',i_port='',content='',sendmail=0):
    # if project_id:
    #     _log = alertlog(project_id=project_id,statusinfo=content,ip=i_ip,port=i_port,sendmail=sendmail)
    #     _log.save()
    # else:
        if not i_port:
            return 
        project_id = project.objects.filter(domain =i_ip)[0].id
        _log = alertlog(project_id=project_id,statusinfo=content,ip=i_ip,port=i_port,sendmail=sendmail)
        _log.save()
   
@login_required(login_url="/login/")
def warning_log(request):

    return render_to_response('log.html' ,{'notiy_rules':''},context_instance=RequestContext(request))

@login_required(login_url="/login/")
def get_warning_log(request):

    userid=1  
    check_type = request.GET.get('check_type', '')

    try:

        res = []
        
        if check_type =='portcheck':
            portcheck_list =   project.objects.values_list('id',flat=True).filter(ports_check=1)
            data = alertlog.objects.all().order_by('-insert_time')[:300]
            for i in data:

                if i.project_id in portcheck_list:
                    _res={'project_id':i.project_id,
                    'statusinfo':i.statusinfo,
                    'timestamp':str(i.insert_time),
                    'ip_port':i.ip+':'+i.port,
                    'tmp':'x',
                    }
                    res.append(_res)

        if check_type =='sslcheck':
            sslcheck_list =   project.objects.values_list('id',flat=True).filter(ports_check=0)
            data = alertlog.objects.all().order_by('-insert_time') 
             
            for i in data:

                if i.project_id    in sslcheck_list:
                    _res={'project_id':i.project_id,
                    'statusinfo':i.statusinfo,
                    'timestamp':str(i.insert_time),
                    'ip_port':i.ip+':'+i.port,
                    'tmp':'x',
                    }
                    res.append(_res)
        return HttpResponse(json.dumps({'result':True,'data':res})) 
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'result':False,'data':str(e)}))
 