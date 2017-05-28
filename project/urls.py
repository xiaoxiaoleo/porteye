from django.conf.urls import patterns, include, url 
# from django_cas.views import login,logout  
# from django.views.decorators.csrf import csrf_exempt 
# from account import views
from project import views
urlpatterns = patterns('',
#     url(r'^$', views.index), 
     url(r'^$', views.index), 
     # url(r'^certs$', views.certs), 
 
      url(r'^getlogs$', views.get_warning_log),  
 
     url(r'^create$', views.create),  
 
     url(r'^createproject$', views.createproject),  
     url(r'^delproject$', views.delproject),  
 
)
