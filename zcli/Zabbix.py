from ClsDict import ClsDict
from Tools import *


class Zabbix(object):

    def __init__(self, zapi, rpc_callback):
        """Class takes zapi instance and an rpc helper function"""
        self.rpc = rpc_callback
        self.zapi = zapi

    @property
    @register_object
    def template(self):
        return self.template

    @template.setter
    def template(self, template):
        if isinstance(template, ClsDict):
            self._template = template
        elif isinstance(template, dict):
            self._template = ClsDict(template)
        else:
            # Load into template
            try:
                self.rpc(self.zapi, 'templet.get',
                         'output=extend;templateids=[10165];'
                         'selectHttpTests=extend;selectTriggers=extend')
            except:
                raise TypeError('Unsupported Template Type')

    @staticmethod
    def objects():
        return globs(__name__, 'object')
