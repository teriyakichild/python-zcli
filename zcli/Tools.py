

_actions = {}
_objects = {}


# Used to register available methods for parsing opts.
def register_action(funct):
    global _actions
    _actions.setdefault(funct.__module__, [])
    _actions[funct.__module__].append(funct.__name__)
    return funct


# Used to register available methods for parsing opts.
def register_object(funct):
    global _objects
    _objects.setdefault(funct.__module__, [])
    _objects[funct.__module__].append(funct.__name__)
    return funct


def globs(module, globtype):
    try:
        glob = {'object': '_objects',
                'action': '_actions'}[globtype]

        return globals()[glob][module]
    except:
        return []
