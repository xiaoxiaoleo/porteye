

def list_ip(request):
    allip =OpenPort.objects.values_list('ip',flat=True).order_by('last_checkdetail_time').distinct()
    return HttpResponse(json.dumps({'result':True,'data':allip})) 
