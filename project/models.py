# encoding:utf-8
from django.db import models  
import datetime
from django.utils.timezone import now
 
class alertlog (models.Model):
    project_id = models.IntegerField()
    ip = models.CharField(max_length=18,blank=True,default='') 
    port =  models.CharField(max_length=10, default='')
    statusinfo = models.CharField(max_length=512,blank=True)
    #timestamp =  models.IntegerField()
    insert_time = models.DateTimeField(default = now)
    #last_time = models.DateTimeField(null=True, blank=True,default = datetime.datetime.now())
    sendmail = models.IntegerField(max_length=1,default=0)  

 