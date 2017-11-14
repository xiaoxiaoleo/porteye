#!/usr/bin/env python
# -*- coding: utf-8 -*-  
from django import template
register = template.Library()
#from app.utils import *
#from app.forms import SCAN_DEPTH_LIST
#try:
#    from json import json
#except ImportError:
#    import json
#import  oldjson
#import json
from os import path
from django.conf import settings
from django.template.defaulttags import register
 
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def cut_string(st):
    if len(st) > 20:
        return st[:20]
    else:
        return ''