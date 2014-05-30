from ClsDict import ClsDict
from Tools import *


## Generator methods ##
@register_object
def template(rpc_callback, obj=None, id=None):
    if id:
        template = Template(rpc_callback=rpc_callback)
        template[template.zid] = id
        template.load()
    elif obj:
        if isinstance(obj, dict):
            template = Template(obj, rpc_callbakc=rpc_callback)
    return template


@register_object
def httptest(rpc_callback, obj=None, id=None):
    if id:
        httptest = HttpTest(rpc_callback=rpc_callback)
        template[template.zid] = id
        httptest.load()
    elif obj:
        if isinstance(obj, dict):
            httptest = HttpTest(obj, rpc_callback=rpc_callback)
    return httptest

def objects():
    return globs(__name__, 'object')


class ZabbixObjBase(ClsDict):

    def __init__(self, *args, **kwargs):
        """Class takes zapi instance and an rpc helper function"""
        # rpc callback takes
        # str: object.action  example: template.get
        # str: query options query string
        if 'rpc_callback' not in kwargs:
            raise ValueError('rpc_callback is None')
        super(ZabbixObjBase, self).__init__(*args, cls_properties=['rpc',
                                                                   'loaded',
                                                                   '_objects_plural',
                                                                   '_objects'])
        try:
            self[self.zid]
            self.loaded = True
        except:
            self.loaded = False
        self.rpc = kwargs['rpc_callback']
        global objects
        self._objects_plural = [x.lower() + 's' for x in objects()]
        self._objects = [x.lower() for x in objects()]

    def load(self):
        try:
            # rpc callback with rpc method[object.get], and params sub'd for id field
            resp = self.rpc(self.zget['method'],
                            [x.format(id=self[self.zid])
                             for x in self.zget['params']])
            for obj in resp:
                for param, val in obj.iteritems():
                    # look for sub structures and instantiate as Zabbix.Object classes
                    if param.lower() in self._objects_plural:
                        obj_funct = globals()[param.lower()[:-1]]
                        if isinstance(val, list):
                            for i, item in enumerate(val):  # update with Zabbix.Object
                                val[i] = obj_funct(self.rpc, obj=item)
                            self[param] = val
                        else:
                            self[param] = obj_function(self.rpc, obj=val)
                    elif param.lower() in self._objects:
                        print(param)
                    else:
                        self[param] = val
            self.loaded = True
        except:
            raise


class Template(ZabbixObjBase):

    zget = {'method': 'template.get',
            'params': ['output=extend',
                       'templateids=[{id}]',
                       'selectHttpTests=extend',
                       'selectTriggers=extend']}

    zupdate = {'method': 'template.update',
               'params': ''}

    zcreate = {'method': 'template.create',
               'params': ''}

    zid = 'templateid'


class HttpTest(ZabbixObjBase):

    zget = {'method': 'httptest.get',
            'params': ['output=extend',
                       'httptestids=[{id}]',
                       'selectSteps=extend']}

    zupdate = {'method': 'httptest.update',
               'params': ''}

    zcreate = {'method': 'httptest.create',
               'params': ''}

    zid = 'httptestid'
