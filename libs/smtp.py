#!/usr/bin/env python
# -*- coding: utf-8 -*-
#导入smtplib和MIMEText
import smtplib,sys 
from email.mime.text import MIMEText 

from hconfig import  mailto_list,mail_host,mail_user,mail_pass,mail_postfix


class SenderEmail:

    def __init__(self, mailto_list,mail_host,mail_user,mail_pass,mail_postfix
):
        self.mailto_list = mailto_list
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.mail_postfix = mail_postfix

    def send_mail(self, sub, content):
        # mailto_list=mailto_list
        #设置服务器，用户名、口令以及邮箱的后缀
        # mail_host=mail_host
        # mail_user=mail_user
        # mail_pass=mail_pass
        # mail_postfix=mail_postfix
        #send_mail("aaa@126.com","sub","content")
        me = self.mail_user+"<"+self.mail_user+"@"+self.mail_postfix+">"
        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(self.mailto_list)
        #print msg
        try:
            s = smtplib.SMTP_SSL()
            s.connect(self.mail_host)
            s.login(self.mail_user,self.mail_pass)
            s.sendmail(me, self.mailto_list, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            return False


if __name__ == '__main__':
    if SenderEmail(mailto_list,mail_host,mail_user,mail_pass,mail_postfix).send_mail(u'HUOBI 端口检测报警',u'xxxxxxcontentxxxxxxx'):
        print u'发送成功'
    else:
        print u'发送失败'