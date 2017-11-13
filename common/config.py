cpath = '/Users/liyueke/Code/porteye'
xpython='/Users/liyueke/Code/env-porteye/bin/python'

master_ip = '127.0.0.1'
master_server = '%s:8000' % master_ip

#mailconfig#
mail_host="smtp.exmail.xx.com"
mail_user="xx@x.com"
mail_pass="xx"
mail_postfix="xx.com"
mailto_list=["xx@xx.com"]
#mailconfig#


mysql_config = {
    'user': 'root',
    'host': '127.0.0.1',
    'port': 3306,
    'passwd': '',
    'charset': 'utf-8',
    'db': 'porteye'
}

masscan_dir = cpath + "tools/masscan/"

distribute_server_list = ['127.0.0.1:8000',]

notify_rule =  []

FLOWER_API  = '%s:5555' % master_ip
 


