from ClsDict import ClsDict
from Tools import *


## Object Generator Methods ##
@register_object
def template(rpc_callback, obj=None, id=None):
    if id:
        templateObj = Template(rpc_callback=rpc_callback)
        templateObj[templateObj._zid] = id
        templateObj.load()
    elif obj:
        if isinstance(obj, dict):
            templateObj = Template(obj, rpc_callbakc=rpc_callback)
            templateObj.load()
    return templateObj


@register_object
def httptest(rpc_callback, obj=None, id=None):
    if id:
        httptestObj = HttpTest(rpc_callback=rpc_callback)
        httptestObj[httptestObj._zid] = id
        httptestObj.load()
    elif obj:
        if isinstance(obj, dict):
            httptestObj = HttpTest(obj, rpc_callback=rpc_callback)
            httptestObj.load()
    return httptestObj


@register_object
def trigger(rpc_callback, obj=None, id=None):
    if id:
        triggerObj = Trigger(rpc_callback=rpc_callback)
        triggerObj[triggerObj._zid] = id
        triggerObj.load()
    elif obj:
        if isinstance(obj, dict):
            triggerObj = Trigger(obj, rpc_callback=rpc_callback)
            triggerObj.load()
    return triggerObj


def objects():
    return globs(__name__, 'object')


#### Base Class ####
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
                                                                   '_objects',
                                                                   '_depends',
                                                                   '_callback_ran'])
        self.rpc = kwargs['rpc_callback']

        self._depends = {}  # store deps as sub-object deps are created
        self._callback_ran = False

        global objects
        self._objects_plural = [x.lower() + 's' for x in objects()]
        self._objects = [x.lower() for x in objects()]

    def load(self):
        try:
            # rpc callback with rpc method[object.get], and params sub'd for id field
            resp = self.rpc(self._zget['method'],
                            [x.format(id=self[self._zid])
                             for x in self._zget['params']])
            for obj in resp:
                for param, val in obj.iteritems():
                    # look for sub structures and instantiate as Zabbix.Object classes

                    if param.lower() in self._objects_plural:
                        obj_funct = globals()[param.lower()[:-1]]
                        if isinstance(val, list):
                            for i, item in enumerate(val):  # update with Zabbix.Object
                                val[i] = self.add_dependancy(obj_funct, item)
                            self[param] = val
                        else:
                            self[param] = self.add_dependancy(obj_funct, val)
                    elif param.lower() in self._objects:
                        print(param)
                    else:
                        self[param] = val
            self._callback_ran = True
        except:
            raise

    @property
    def depends(self):
        """A list of dependancies"""
        return self._depends  # initialized in __init__

    @depends.setter
    def depends(self, depends):
        self._depends = depends

    def add_dependancy(self, object_function, val):
        """Add a sub item and track it as a dependancy"""
        if not id(val) in self._depends:
            obj = object_function(self.rpc, obj=val)
            self.depends[id(val)] = obj
            return obj

    @property
    def loaded(self):
        """Loaded if true"""
        if self[self._zid] and self._callback_ran:
            return True
        else:
            return False


class Template(ZabbixObjBase):

    _zget = {'method': 'template.get',
             'params': ['output=extend',
                        'templateids=[{id}]',
                        'selectHttpTests=extend',
                        'selectTriggers=extend']}

    _zupdate = {'method': 'template.update',
                'params': ''}

    _zcreate = {'method': 'template.create',
                'params': ''}

    _zid = 'templateid'


class HttpTest(ZabbixObjBase):

    _zget = {'method': 'httptest.get',
             'params': ['output=extend',
                        'httptestids=[{id}]',
                        'selectSteps=extend']}

    _zupdate = {'method': 'httptest.update',
                'params': ''}

    _zcreate = {'method': 'httptest.create',
                'params': ''}

    _zid = 'httptestid'


class Trigger(ZabbixObjBase):

    _zget = {'method': 'trigger.get',
             'params': ['output=extend',
                        'triggerids=[{id}]',
                        'selectFunctions=extend',
                        'expandExpression=True',
                        'expandComment=True',
                        'expandDescription=True']}

    _zupdate = {'method': 'trigger.update',
                'params': ''}

    _zcreate = {'method': 'trigger.create',
                'params': ''}

    _zid = 'triggerid'
