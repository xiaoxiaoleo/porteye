from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
# Create your models here.
class port_alive_project(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=80)
    port = models.IntegerField()
    domain = models.CharField(max_length=80)
    check_frequency = models.IntegerField() # fenzhong
    notify_rule_id = models.IntegerField()
    create_time = models.CharField(max_length=30)
    status = models.IntegerField() # 0=wait for upload  1=wait for checking 2=normal 3=warning 4=error 5=expired
    statusinfo = models.CharField(max_length=512,blank=True)
    ports_check = models.BooleanField(default=False) 
    main_id = models.IntegerField(default=0)

class port_monitor(models.Model):
	#id is main id
    name = models.CharField(max_length=80)
    ip_range = models.CharField(max_length=80)
    check_frequency = models.IntegerField(default = 0 ) # fenzhong
    create_time = models.DateTimeField(default = now)
    remarks  = models.CharField(max_length=512,blank=True)
    fnascan_check = models.BooleanField(default=True) 
    masscan_check = models.BooleanField(default=True) 
    last_check_time = models.DateTimeField(default = now)
 



class FnascanResult(models.Model):
    """
    save fnscan port scan results
    """
    project_id = models.IntegerField()
    last_check_time =models.DateTimeField(null=True, blank=True )
    insert_time = models.DateTimeField(null=True, blank=True )
    update_time = models.DateTimeField(null=True, blank=True ,default = now)
    # update_service_name_time = models.DateTimeField(null=True, blank=True )
    # update_web_title_time = models.DateTimeField(null=True, blank=True )
    # update_port_status_time = models.DateTimeField(null=True, blank=True )

    ip = models.CharField(max_length=18,blank=True) 
    port =  models.CharField(max_length=10)
    service_name = models.TextField(null=True, blank=True, default='')
    web_title = models.TextField(null=True, blank=True, default='')
    service_detail = models.TextField(null=True, blank=True, default='')
    port_status = models.BooleanField(default=True) 
    ip_status = models.BooleanField(default=True) 

    # comment = models.TextField(null=True, blank=True, default='') #

class OpenPort(models.Model):
    """
    save open port results
    """
    project_id = models.IntegerField()
    lastcheckts=models.IntegerField(default=0)
    insert_time = models.DateTimeField(null=True, blank=True )
    update_time = models.DateTimeField(null=True, blank=True ,default = now)
    update_banner_time = models.DateTimeField(null=True, blank=True )
    last_checkdetail_time = models.DateTimeField(null=True, blank=True )
    ip = models.CharField(max_length=18,blank=True) 
    port =  models.CharField(max_length=10)
    banner = models.TextField(null=True, blank=True, default='')
    port_status = models.BooleanField(default=True) 
    findby  =  models.CharField(max_length=10,default='')
    #updateby  =  models.CharField(max_length=10,default='')
    remarks = models.TextField(blank=True,default='')

# class FnascanMetadata(models.Model):
#     """
#     save fnscan   scan results
#     """
#     project_id = models.IntegerField()
#     lastcheckts=models.IntegerField(default=0)
#     insert_time = models.DateTimeField(null=True, blank=True,default = now)
    
#     portinfo = models.TextField(null=True, blank=True, default='')
#     port_data  = models.TextField(null=True, blank=True, default='') 
#     statistics = models.TextField(null=True, blank=True, default='')
  
# wyportmap models
class ResultIp(models.Model):
    taskid = models.IntegerField(blank=True, null=True)
    inserted = models.DateTimeField(blank=True, null=True)
    domain = models.CharField(max_length=256, blank=True, null=True)
    address = models.CharField(max_length=32, blank=True, null=True)
    is_up = models.IntegerField(blank=True, null=True)
    os = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_ip'

# wyportmap models
class ResultPorts(models.Model):
    taskid = models.IntegerField(blank=True, null=True)
    inserted = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    service = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=12, blank=True, null=True)
    protocol = models.CharField(max_length=12, blank=True, null=True)
    product = models.CharField(max_length=64, blank=True, null=True)
    product_version = models.CharField(max_length=64, blank=True, null=True)
    product_extrainfo = models.CharField(max_length=128, blank=True, null=True)
    scripts_results = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_ports'

# 
class IpRemarks(models.Model):
    ip_addr  = models.CharField(max_length=80,default = '')
    create_time = models.DateTimeField(default = now)
    business  = models.CharField(max_length=512,blank=True) #  the server for what 
    own  = models.CharField(max_length=512,blank=True)  # 
    remarks  = models.CharField(max_length=512,blank=True,default = '') #
    doamin  = models.CharField(max_length=512,blank=True,default = '') # domain name