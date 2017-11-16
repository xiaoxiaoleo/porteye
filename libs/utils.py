# encoding:utf-8
# code by evileo

import urllib2
import urllib
import json

def postHttp(url, postdata):
    #url编码
    postdata=urllib.urlencode(postdata)
    #enable cookie
    request = urllib2.Request(url,postdata)
    response=urllib2.urlopen(request)
    #print response

def getJsonHttp(url):  
    result = urllib2.urlopen(url)
    return json.loads(result.read())

# [ '1','2']  to  [1,2]
def list_str2int(lista):
    listb = []
    for i in lista:
        j = int(i)
        listb.append(j)
    return listb

def list_int2str(lista):
    listb = []
    for i in lista:
        j = str(i)
        listb.append(j)
    return listb


def sort_masscan(tmp):
    d = {}
    for v in tmp:
        a = v.split(':')
    if d.has_key(a[0]):
        d[a[0]] += [a[1]]
    else:
        d[a[0]] = [a[1]]

    return d
