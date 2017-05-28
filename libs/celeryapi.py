import requests  as MyReq

#from libs.log import logger
import json

from hconfig import FLOWER_API  
FLOWER_API = "http://%s" %  FLOWER_API
headers = {'Content-type': 'application/json', 'Accept': 'text/plain','Connection':'close'}
def K_send_task(data,task_name):
	#worker not run {u'task-id': u'fdb79f4b-5f82-4c42-8f5e-b643c492c96c', u'state': u'PENDING'}
    #worker run 
	r = MyReq.post(FLOWER_API + '/api/task/send-task/%s' % task_name, data=json.dumps(data), headers=headers)
    #print r.status_code
	#logger.info('send %s %s %d' % (_subtask.attack_type,_subtask.attack_target,r.status_code))#r.json()
	return r.json()

def  K_get_result(task_id):
	r = MyReq.get(FLOWER_API + '/api/task/result/'+task_id,headers=headers)
	return r.json()
