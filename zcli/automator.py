import json
from tools import ClsDict


methods = []


def register(funct):
    global methods
    methods.append(funct.__name__)
    return funct


class ZabbixAutomator(object):

    def __init__(self, zapi, rpc_callback):
        """Class takes zapi instance and an rpc helper function"""
        self.rpc = rpc_callback
        self.zapi = zapi

    @property
    @register
    def template(self):
        return self.template

    @template.setter
    def template(self, template):
        self.template = template

    @staticmethod
    def objects():
        global methods
        return methods
