from pyzabbix import ZabbixAPI
from config import config

def comp(list1, list2):
    status = True
    missing = []
    for val in list1:
        if val not in list2:
            missing.append(val)
            status = False
    return {'status':status,'missing':missing}

c = config()
hostgroups = {}
for env in c.sections():
  c.set(env)
  zapi = ZabbixAPI(c.host,verify=False)

  # Login to the Zabbix API
  zapi.login(c.username, c.password)
  print zapi.user.get()
  args_arr = {'output':'extend'}
  method_arr = ['host','get']
  for argument in args_arr:
    print [a[0] for a in argument.split(',')]
  print args_arr
  func = getattr(getattr(zapi,method_arr[0],None),method_arr[1],None)
  if callable(func):
    print func()

