from django.conf.urls import patterns, include, url
from web import views, views_api, views_main


urlpatterns = patterns('',
     url(r'^$', views.index), 
 	 url(r'^getproject$', views.getproject), 

       
     url(r'^openport$', views.openport),  
     url(r'^all_project', views.all_project),
     url(r'^alivehost$', views.alivehost),  
     url(r'^singleopenport$', views.singleopenport),  
     url(r'^ipdetail$', views.ipdetail),  
    
     # API
     url(r'^list_all_ip$', views_api.list_all_ip),
     url(r'^list_alive_host$', views_api.list_alive_host),
     url(r'^list_all_ip_range$', views_api.list_all_ip_range),
     url(r'^list_all_open_port$', views_api.list_all_open_port),
     url(r'^ip_address_to_project_id$', views_api.ip_address_to_project_id),
     url(r'^upload_open_port$', views_api.upload_open_port),
     url(r'^upload_alive_host$', views_api.upload_alive_host),
     url(r'^upload_fnascan_result', views_api.upload_fnascan_result),


     url(r'^getlogs$', views_main.get_warning_log),
     url(r'^create', views_main.create),
     # url(r'^add_domain$', views_main.add_domain),
     # url(r'^create_project$', views_main.create),
     # url(r'^add_ip_range', views_main.add_ip_range),
     url(r'^delproject$', views_main.delproject),
)
