from django.conf.urls import patterns, include, url 
# from django_cas.views import login,logout  
# from django.views.decorators.csrf import csrf_exempt 
from portmonitor import views

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

#     url(r'^modify$', views.modify),   
)
