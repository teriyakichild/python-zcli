from __future__ import print_function
from pyzabbix import ZabbixAPI, ZabbixAPIException
from config import config
from automator import ZabbixAutomator
import argparse
import json
import getpass
import sys
import os


def cli():
    c = config()
    envs = c.sections if len(c.sections) else ['Set in conf',]
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--debug", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-e", "--environment", choices=envs,
                        help="Which environment to connect to ({0})".
                             format(','.join(envs)))
    parser.add_argument("-h", "--host", default=os.environ.get('ZA_HOST', None),
                        help="Zabbix API URL; overrides environment.host" +
                        "full URL format https://zabbixhost.example.com")
    parser.add_argument("-u", "--user", default=os.environ.get('ZA_USER', None),
                        help="Zabbix API user; overrides environment.password")
    parser.add_argument("-p", "--password", default=None,
                        help="Zabbix API password; set on CLI ZA_PASSWORD or" +
                        "prompt overrides environment.password")
    subparsers = parser.add_subparsers(help='sub-command help',
                                       dest="subparser_name")

    method_parser = subparsers.add_parser('method', help='Zabbix API RPC mode')
    method_parser.add_argument("method",
                               help="Zabbix API method (host.get,hostgroups.get," +
                               "usergroups.get)")
    method_parser.add_argument("arguments", nargs="?",
                               help="Zabbix API arguments for method",
                               default="output=extend")

    abstract_objects = ['']
    export_parser = subparsers.add_parser('export',
                                          help='Friendly object export commands')
    export_parser.add_argument('--object', choices=ZabbixAutomator.objects())
    export_parser.add_argument('-O', '--file', type=argparse.FileType(mode='w'),
                               help='Export to file')

    parser.add_argument('--help', action='store_true')

    try:
        args = parser.parse_args()
    except IOError as e:
        print("Could not open file %s: %s" % (e.filename, e.strerror),
              file=sys.stderr)
        sys.exit(1)

    if args.help:
        parser.print_help()

    if args.debug:
        print("Debug enabled", file=sys.stderr)

    if args.environment:
        c.env = args.environment

    if args.host:
        c.host = args.host
    else:
        try:
            if not c.host or c.host == 'ask':
                c.host = raw_input('Host: ')
        except Exception:
            print('No host defined on command line or config file', file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    if args.user:
        c.username = args.user
    else:
        try:
            if not c.username or c.username == 'ask':
                c.username = raw_input('Username: ')
        except Exception:
            print('No user defined on command line or config file', file=sys.stderr)
            parser.print_help()
            sys.exit(1)

    tmp_pass = os.environ.get('ZA_PASSWORD', None)
    if tmp_pass:
        c.password = tmp_pass
    else:
        try:
            if args.password or c.password == 'ask':
                c.password = getpass.getpass()
        except Exception:
            print('No password defined on command line or config file', file=sys.stderr)
            parser.print_help()
            sys.exit(1)

    zapi = ZabbixAPI(c.host)
    zapi.session.verify = False
    # Login to the Zabbix API
    try:
        zapi.login(c.username, c.password)
    except Exception as e:
        if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
            try:
                zapi = ZabbixAPI(c.host + '/zabbix')
                zapi.session.verify = False
                zapi.login(c.username, c.password)
            except Exception as e:
                if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
                    print("Invalid Host url", file=sys.stderr)
                    exit(1)
                raise
        else:
            raise

    if args.subparser_name == 'method':
        return json.dumps(rpc(zapi, args.method, args.arguments), indent=2)
    elif args.subparser_name == 'export':
        return export(zapi, args)


def rpc(zapi, rpc_method, args):
    if '.' in rpc_method:
        method_arr = rpc_method.split('.')
    args_arr = args.split(';')
    arguments = {}
    for argument in args_arr:
        if '=' in argument:
            tmp = [a for a in argument.split('=')]
            try:
                value = eval(tmp[1])
            except (NameError, SyntaxError):
                value = tmp[1]
            arguments[tmp[0]] = value
        elif 'delete' in method_arr[1]:
            arguments = argument

    func = getattr(getattr(zapi, method_arr[0], None), method_arr[1], None)
    try:
        if isinstance(arguments, str):
            print(arguments)
            ret = func(arguments[0])
        else:
            ret = func(**arguments)
    except ZabbixAPIException as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    return ret


def export(zapi, args):
    """Export zapi objects to stdout or file"""
    #TODO(nickshobe) Ready for recursive exporting
    # It looks like I can query web scenario objects by application name, or id not
    # template id
    obj = {'test': 'bob'}
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
