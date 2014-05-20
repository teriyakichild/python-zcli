from pyzabbix import ZabbixAPI, ZabbixAPIException
from config import config
import argparse
import json
import getpass

def cli():
  c = config()
  envs = c.sections()
  parser = argparse.ArgumentParser()
  parser.add_argument("--debug", help="increase output verbosity",
                    action="store_true")
  parser.add_argument("-e","--environment", help="Which environment to connect to ({0})".format(','.join(envs)))
  parser.add_argument("method", help="Zabbix API method (host.get,hostgroups.get,usergroups.get)")
  parser.add_argument("arguments", nargs="?", help="Zabbix API arguments for method", default="output=extend")
  args = parser.parse_args()
  if args.debug:
    print "verbosity turned on"
  if args.environment not in envs:
    return 'Error: {0} not in environment list'.format(args.environment)
  c.set(args.environment)
  if c.host == 'ask':
    c.host = raw_input('Host: ')
  if c.username == 'ask':
    c.username = raw_input('Username: ')
  if c.password == 'ask':
    c.password = getpass.getpass()
  zapi = ZabbixAPI(c.host,verify=False)
  # Login to the Zabbix API
  zapi.login(c.username, c.password)

  if '.' in args.method:
    method_arr = args.method.split('.')
  args_arr = args.arguments.split(';')
  arguments = {}
  for argument in args_arr:
     if '=' in argument:
       tmp = [a for a in argument.split('=')]
       try:
         value = eval(tmp[1])
       except (NameError,SyntaxError):
         value = tmp[1]
       arguments[tmp[0]] = value
     else:
       if 'delete' in method_arr[1]:
         arguments = argument
  func = getattr(getattr(zapi,method_arr[0],None),method_arr[1],None)
  try:
    if type(arguments) is str:
      print arguments
      ret = func(arguments[0])
    else:
      ret = func(**arguments)
  except ZabbixAPIException as e:
    print e
    exit(1)
  return json.dumps(ret,indent=2)
