from django.conf.urls import patterns, include, url
from web import views, views_api, views_main


urlpatterns = patterns('',
     url(r'^$', views.index), 
 	 url(r'^getproject$', views.getproject), 
     url(r'^uploadopenport$', views.uploadopenport), 
     url(r'^uploadfnascanresult$', views.uploadfnascanresult), 
       
     url(r'^openport$', views.openport),  
     url(r'^main_project$', views.main_project),  
     url(r'^alivehost$', views.alivehost),  
     url(r'^singleopenport$', views.singleopenport),  
     url(r'^ipdetail$', views.ipdetail),  
    
     url(r'^list_all_ip$', views_api.list_all_ip),
     url(r'^list_all_ip_range$', views_api.list_all_ip_range),

     url(r'^getlogs$', views_main.get_warning_log),
     url(r'^create$', views_main.create_portmonitor),
     url(r'^createproject$', views_main.createproject),
     url(r'^delproject$', views_main.delproject),

)
