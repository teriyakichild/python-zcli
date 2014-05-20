import requests
import json

class zabbix:
  host=''
  def _request(self,payload):
    headers = { 'content-type':'application/json' }
    r = requests.post(self.host, data=json.dumps(payload), headers=headers, verify=False)
    return r.json()

  def auth(self,host,username,password):
    self.host=host
    payload = { "jsonrpc": "2.0", "method": "user.login", "params": { "user": username, "password": password }, "id": 1 }
    ret = self._request(payload)
    self.token = ret['result']

  def gettoken(self):
    return self.token

  def getuser(self,username):
    payload = { "jsonrpc":"2.0", "method":"user.get", "params":{ "filter":{ "alias":[username] }, "output":"extend" }, "auth":self.token, "id":2 }
    return self._request(payload)

  def getusergroups(self):
    payload = { "jsonrpc":"2.0", "method":"usergroup.get", "params":{ "select_users":"refer", "output":"extend" }, "auth":self.token, "id":2 }
    try:
      return self._request(payload)['result']
    except:
      return None
  def gethostgroups(self):
    payload = { "jsonrpc":"2.0", "method":"hostgroup.get", "params":{ "output":"extend" }, "auth":self.token, "id":2 }
    try:
      return self._request(payload)['result']
    except:
      return None

  def adduser(self,username,fname,lname,role):
    if role == 7:
      usrgrps = { "usrgrpid":"7", "name":"Zabbix administrators" }
      type = "3"
    elif role == 13:
      usrgrps = { "usrgrpid":"13", "name":"Local Users" }
      type = "1"
    elif role == 8:
      usrgrps = { "usrgrpid":"8", "name":"Guest" }
      type = "1"
    payload = { "jsonrpc":"2.0", "method":"user.create", "params":[{ "usrgrps": [usrgrps], "alias":username, "name":fname, "surname":lname, "passwd":"zabbix", "url":"", "autologin":"0", "autologout":"600", "lang":"en_US", "refresh":"90", "type":type, "theme":"default", "attempt_failed":"0", "attempt_ip":"0", "attempt_clock":"0", "rows_per_page":"50" }], "auth":self.token, "id":3 }
    return self._request(payload)

  def update(self,userid):
    payload =  { "jsonrpc":"2.0", "method":"user.update", "params":{ "userid": userid, "lang": "en_US" }, "auth":self.token,  "id":2 }
    return self._request(payload)

if __name__ == "__main__":
  z = zabbix()
  z.auth()
  print z.getusergroups()
  check = z.getuser('apiuser')
  print check 
#  export = z.export_config()
#  print 'Export: '+ export
#  z.import_config(export)
#
#  newexport = z.export_config()
#  print newexport
  
