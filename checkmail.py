# encoding:utf-8

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','porteye.settings')
import django
django.setup()

from libs.smtp import SenderEmail

from project.models import alertlog
from libs.mylogger import mylogger
logger = mylogger('checkmail.py')
from hconfig import  mailto_list,mail_host,mail_user,mail_pass,mail_postfix
from hconfig import master_server 
def check_sendmail():
    # mail_log = ''

    # mailcontent = ""

    # """
    # ip,port

    # """
    logger.info("check  and send mail")
    mail_html = """<!DOCTYPE html>
              <html>

              <body>

              %s

              </body>
              </html>"""

    mail_table = """
            <table border="1">
              <caption>%s</caption>
               <thead>
                  <tr>
                     <th>project id</th>
                     <th>ip</th>
                     <th>port</th>
                     <th>info  </th>
                     <th>find time </th>
                  </tr>
               </thead>
               <tbody>
                %s
               </tbody>
            </table>"""
    alert_list = alertlog.objects.filter(sendmail=1).order_by('ip')

    # _output  = '<tr>'
    if len(alert_list) < 1:
        logger.warning("no alert log need send mail")
        return

    ip_list = list(set(alertlog.objects.filter(sendmail=1).values_list('ip', flat=True)))
    big_output = ''
    for ip_address in ip_list:

      sigle_alert_list = alertlog.objects.filter(sendmail=1,ip=ip_address).order_by('info')
      #print sigle_alert_list 

      _output  = ''
      for _alert  in sigle_alert_list:
        _output  = _output +   '<tr>'
        _output = _output +   '<td><a href="http://'+master_server+'/project/report?id='+ str(_alert.project_id)  +'>' + str(_alert.project_id) + '</a></td>'
        _output = _output +   '<td>' + str(_alert.ip) + '</td>'
        _output = _output +   '<td>' + str(_alert.port) + '</td>'
        _output = _output +   '<td>' + _alert.statusinfo + '</td>'
        _output = _output +   '<td>' + str(_alert.insert_time) + '</td>'
        _output = _output +   '</tr>'
        #print _output
      mail_table1 = mail_table % (ip_address,_output)
      #print mail_table1
      big_output = big_output + mail_table1
    #print _output
    mailcontent = mail_html %  big_output

    #print mailcontent


    
    #if SenderEmail().send_mail(u'HUOBI 端口检测告警'   ,u'%s' % mailcontent):
    if SenderEmail(mailto_list,mail_host,mail_user,mail_pass,mail_postfix).send_mail(u'HUOBI 端口检测告警'   ,u'%s' % mailcontent):
       
        mail_log =  'mail send success'
    else:
        mail_log = 'mail send error!'

    _t = alertlog.objects.all().update(sendmail=2)
     


if __name__ == '__main__':
	check_sendmail()