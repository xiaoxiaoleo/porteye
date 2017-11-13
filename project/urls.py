from django.conf.urls import patterns, url
from project import views
urlpatterns = patterns('',
     url(r'^$', views.index),
     url(r'^getlogs$', views.get_warning_log),
     url(r'^create$', views.create),
     url(r'^createproject$', views.createproject),  
     url(r'^delproject$', views.delproject),  
 
)
