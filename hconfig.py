cpath = '/home/leo/Desktop/sslcloud/'
master_ip = '127.0.0.1'

xpython='/home/leo/Desktop/envxlcscan/bin/python'

define_modules={'basic':'--certinfo_basic ',
                'ccs':'--openssl_ccs ',
                'hsts':'--hsts ',
                'heartbleed':'--heartbleed ',
                'poodle':'--poodle ',
                'ports_check':'--ports_check ',
                }



master_server = '%s:8000' % master_ip


#mailconfig#
mail_host="smtp.exmail.xx.com"
mail_user="xx@x.com"
mail_pass="xx"
mail_postfix="xx.com"
mailto_list=["xx@xx.com"]
#mailconfig#


masscan_dir = cpath + "masscan/"

distribute_server_list = ['127.0.0.1:8000',]

notify_rule =  []


FLOWER_API  = '%s:5555' % master_ip

wyportmap_dir = cpath + 'wyportmap/wyportmap.py'


