"""porteye URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from web.forms import BootstrapAuthenticationForm
from django.contrib import admin
from django.contrib.auth import views as login_views
from datetime import datetime

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',include('web.urls')),
    url(r'^login/$',
         login_views.login ,
        {
            'template_name': 'auth/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        login_views.logout,
        {
            'template_name': 'auth/logout.html',
            'next_page': '/',   
        },
        name='logout'), 
]
