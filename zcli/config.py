import ConfigParser

class config:
  def __init__(self):
    # Config Parse stuff
    self.Config = ConfigParser.ConfigParser()
    self.Config.read('/etc/zcli.conf')
  def set(self,env):
    if env in self.sections():
      try:
        self.host = self.Config.get(env,'host')
        self.username = self.Config.get(env,'username')
        self.password = self.Config.get(env,'password')
      except ConfigParser.NoSectionError:
        exit('Check config file: /etc/zcli.conf')
      return True
    else:
      return False
  def host(self):
    return self.host
  def username(self):
    return self.username
  def password(self):
    return self.password
  def sections(self):
    return self.Config.sections()
