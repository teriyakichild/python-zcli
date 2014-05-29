

# Why cls_state... cls_state is a portable attrdict
class ClsDict(dict):
    """This is an attrdict implementation that provides:
    * property access for dict elements
    * overrides for properties
    *
    * Override getitem, setitem, getattr, and setattr to provide the following behaviors:
       @property decorators take precidence over dict items... and are always called.
       @prop.setter decorators take precidence and can call self['key'] to set dict vals.
       self.cls_properties['key'] to prevent key from being auto saved self['key']
       self.key == self['key'] without self.cls_properties or @property
       reserved keys are:
           * cls_properties - use to always treat properties['name'] as a property only.
           * _cls_seen_flags - flag list to prevent inf looping
           * CLSDICT_PROPERTIES
    """

    # CLS_ITEMS kept from iter and dict, but not properties
    CLSDICT_PROPERTIES = ['cls_properties', '_cls_seen_flags',
                          '__dict__', '__members__', '__methods__', '__class__']

    def __init__(self, *args, **kwargs):
        """Build a fancy attrdict like object
            arg0 dict The diction object to instatiate with
            :recurse: True"""
        # Order here is critical
        # 1st
        if not hasattr(self, '_cls_seen_flags'):
            self._cls_seen_flags = []
        # 2nd
        if not hasattr(self, 'cls_properties'):
            self.cls_properties = []
            if 'cls_properties' in kwargs and isinstance(kwargs['cls_properties'], list):
                self.cls_properties = self.cls_properties + kwargs['cls_properties']
        recurse = kwargs['recurse'] if 'recurse' in kwargs else True
        obj = args[0] if len(args) > 0 else {}
        """Recusrively call self to capture all itterable dict and lists"""
        if not recurse:
            for k, v in obj.iteritems():
                self[k] = v
        else:  # recursive option recurses till it hits a non dict or non dict in a list
               # E.G. list in list or object in list or string in list.
               # a dict in a list would still recurse, but not a dict in a list in a list.
               # [{}] > yes
               # [[{}]] > no
               # ['str'] > no
               # [{key:'val'},'str'] > yes, no
            if isinstance(obj, dict):
                for k, v in obj.iteritems():
                    if isinstance(v, dict):
                        self[k] = ClsDict(v)
                    elif isinstance(v, list):  # list in dict
                        nl = []
                        for item in v:
                            if isinstance(item, dict):
                                nl.append(ClsDict(item))
                            else:  # if list in list or string or other... stop recursing
                                nl.append(item)
                        self[k] = nl
                    else:
                        self[k] = v

    def __getattribute__(self, key):
        # prevent recursion loops
        CLSDICT_PROPERTIES = super(ClsDict,
                                         self).__getattribute__('CLSDICT_PROPERTIES')
        if (key == 'cls_properties' or
                key == '_cls_seen_flags' or
                key in CLSDICT_PROPERTIES):
            return super(ClsDict, self).__getattribute__(key)
        else:
            # prevent recursion loops -- local vars for easier use later
            _cls_seen_flags = super(ClsDict, self).__getattribute__('_cls_seen_flags')
            cls_properties = super(ClsDict, self).__getattribute__('cls_properties')
            #__class__ = super(ClsDict, self).__getattribute__('__class__')

            if (key not in _cls_seen_flags and
                (hasattr(self, 'cls_properties') and key in cls_properties) or
                    key in dir(self)):
                try:
                    _cls_seen_flags.append(key)
                    val = super(ClsDict, self).__getattribute__(key)
                except:
                    raise
                finally:
                    _cls_seen_flags.remove(key)

                return val
            else:
                try:
                    return super(ClsDict, self).__getattribute__(key)
                except:
                    return self[key]

    def __setattr__(self, key, val):
        if (key == 'cls_properties' or
                key == '_cls_seen_flags' or
                key in self.CLSDICT_PROPERTIES):
            super(ClsDict, self).__setattr__(key, val)
        else:
            _cls_seen_flags = super(ClsDict, self).__getattribute__('_cls_seen_flags')
            if (key not in _cls_seen_flags and
                    (hasattr(self, 'cls_properties') and key in self.cls_properties or
                     key in dir(self))):

                try:
                    _cls_seen_flags.append(key)
                    super(ClsDict, self).__setattr__(key, val)
                except:
                    raise
                finally:
                    _cls_seen_flags.remove(key)

            else:
                self[key] = val

    def __getitem__(self, key):
        if (key == 'cls_properties' or
                key in self.CLSDICT_PROPERTIES or
                key in dir(self) or
                hasattr(self, 'cls_properties') and key in self.cls_properties):
            if key not in self._cls_seen_flags:
                return getattr(self, key)
            else:
                return super(ClsDict, self).__getitem__(key)
        else:
            return super(ClsDict, self).__getitem__(key)

    def __setitem__(self, key, val):
        if (key == 'cls_properties' or
                key == '_cls_seen_flags' or
                key in self.CLSDICT_PROPERTIES):
            setattr(self, key, val)
        else:
            if (key not in self._cls_seen_flags and
                (key in dir(self) or
                    hasattr(self, 'cls_properties') and key in self.cls_properties)):
                setattr(self, key, val)
            else:
                super(ClsDict, self).__setitem__(key, val)
