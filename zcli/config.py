import ConfigParser


class config(object):

    def __init__(self):
        # Config Parse stuff
        self.Config = ConfigParser.ConfigParser()
        self.Config.read('/etc/zcli.conf')

    @property
    def env(self):
        try:
            return self._env
        except AttributeError:
            return None

    @env.setter
    def env(self, env):
        try:
            if env in self.sections:
                self._env = env
            else:
                raise ConfParser.NoSectionError(env)
            self.host = self.Config.get(env, 'host')
            self.username = self.Config.get(env, 'username')
            self.password = self.Config.get(env, 'password')
        except ConfParser.NoSectionError:
            raise

    @property
    def host(self):
        try:
            return self._host
        except AttributeError:
            try:
                return self.Config.get(self.env, 'host')
            except:
                raise

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def username(self):
        try:
            return self._username
        except AttributeError:
            try:
                user = self.Config.get(self.env, 'username')
                if not user:
                    user = self.Config.get(self.env, 'user')
                return user
            except ConfParser.NoSectionError:
                raise

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def password(self):
        try:
            return self._password
        except AttributeError:
            try:
                return self.Config.get(self.env, 'password')
            except ConfigParser.NoSectionError:
                raise

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def sections(self):
        return self.Config.sections()
