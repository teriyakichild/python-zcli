import json
from Tools import *
from ClsDict import ClsDict
import Zabbix


class ZAutomator(object):

    def __init__(self, rpc_callback):
        """Class takes zapi instance and an RPC helper function"""
        self.rpc = rpc_callback

    #### Internal Properties
    @property
    def bundle(self):
        """A bundle object"""
        return self._bundle

    @bundle.setter
    def bundle(self, bundle):
        """Set a bundle object"""
        if not isinstance(bundle, ClsDict):
            raise ValueError('Type must be a ClsDict child')
        self._bundle = bundle

    #### Actions ####
    @register_action
    def extract(self, obj, id):
        """Extract objects from a Zabbix environment"""
        if obj == 'template':
            bundle = getattr(Zabbix, obj)(self.rpc, id=id)
            import pdb;pdb.set_trace()

    @register_action
    def deploy(self):
        """Deploy a bundle or object to a target Zabbix environment"""
        pass

    #### Objects ####

    #### Internal Methods ####
    def exporter(args):
        """Export zapi objects to stdout or file.
            rpc: loaded rpc callback created with rpc(zapi)
            args: parser.args"""
        #TODO(nickshobe) Ready for recursive exporting
        # It looks like I can query web scenario objects by application name, or id not
        # template id

        retval = json.dumps(obj)
        if args.file:
            try:
                args.file.write(retval)
                retval = ''
            except:
                print("Failed to write to specified file %s: writing to stdout" %
                      args.file.name, sys.stderr)
            finally:
                args.file.close()

        return retval

    def build_bundle(self, bundle_raw):
        """build a bundle from an set of zabbix objects"""
        pass

    def load_bundle(self, bundle_json):
        """Load a bundle from a bundlejson string"""
        pass

    #### Utility Static Methods ####
    @staticmethod
    def objects():
        return Zabbix.objects() + globs(__name__, 'object')

    @staticmethod
    def actions():
        return globs(__name__, 'action')
