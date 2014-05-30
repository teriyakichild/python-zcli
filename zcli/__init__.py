"""Zabbix CLI provides basic RPC queries and import export automation"""
from __future__ import print_function
from pyzabbix import ZabbixAPI, ZabbixAPIException
from config import config
from ZAutomator import ZAutomator
import argparse
import json
import getpass
import sys
import os


def build_parsers(conf):
    """Build parsers for cli"""
    # TODO(Nick) consider moving to
    # usage = "usage: whichboom [-h] [-s | [-h] [-s]] host"
    # description = "Lookup servers by ip address from host file"
    # parser = argparse.ArgumentParser(description=description, usage=usage)

    envs = conf.sections if len(conf.sections) else ['Unset',]
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=__doc__)

    parser.add_argument("--debug", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-e", "--environment",
                        choices=envs,
                        help="Which environment to connect to ({0})".
                        format(','.join(envs)))
    parser.add_argument("-u", "--url",
                        default=os.environ.get('ZA_URL', None),
                        help="(default) Zabbix API URL; overrides environment.url "
                        "full URL format https://zabbixhost.example.com")
    parser.add_argument("-U", "--user",
                        default=os.environ.get('ZA_USER', None),
                        help="Zabbix API user; overrides environment.password")
    parser.add_argument("-p", "--password",
                        default=None,
                        help="Zabbix API password; set on CLI ZA_PASSWORD or "
                        "prompt overrides environment.password")

    subparsers = parser.add_subparsers(dest="subparser_name",)

    method_parser = subparsers.add_parser('method', help='Zabbix API RPC mode')
    method_parser.add_argument('method',
                               help='Zabbix API RPC method (host.get,'
                               'hostgroups.get,usergroups.get)')
    method_parser.add_argument("-a", '--arguments',
                               dest='arguments',
                               default=['output=extend'],
                               help="RPC params", action='append')

    automator_parser = subparsers.add_parser('automator',
                                             help='Friendly object export commands')

    automator_parser.add_argument('--action', choices=ZAutomator.actions(),
                                  required=True,
                                  help='Action to perform')
    automator_parser.add_argument('--object', choices=ZAutomator.objects(),
                                  required=True,
                                  help='Top level zabbix object to fully export '
                                  'usually a template or host with all sub objects '
                                  'Example: --object template')
    automator_parser.add_argument('--id',
                                  required=True,
                                  help='Id attribute for the object query '
                                  'Example: --object template --id 34')

    iogroup = automator_parser.add_mutually_exclusive_group()
    iogroup.add_argument('-o', '--out', type=argparse.FileType(mode='w'),
                         help='Output bundle file')
    iogroup.add_argument('-i', '--in', type=argparse.FileType(mode='r'),
                         help='Input Bundle file')

    return parser


def cli():
    """Main CLI entry"""
    c = config()
    parser = build_parsers(c)

    try:
        args = parser.parse_args(sys.argv[1:])
    except IOError as e:
        print("Could not open file %s: %s" % (e.filename, e.strerror),
              file=sys.stderr)
        sys.exit(1)

    if args.debug:
        print("Debug enabled", file=sys.stderr)

    if args.environment:
        c.env = args.environment

    if args.url:
        c.url = args.url
    else:
        try:
            if not c.url or c.url == 'ask':
                c.url = raw_input('URL: ')
        except Exception:
            print('No url defined on command line or config file', file=sys.stderr)
            #parser.print_help()
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

    zapi = ZabbixAPI(c.url)
    zapi.session.verify = False
    # Login to the Zabbix API
    try:
        zapi.login(c.username, c.password)
    except Exception as e:
        if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
            try:
                zapi = ZabbixAPI(c.url + '/zabbix')
                zapi.session.verify = False
                zapi.login(c.username, c.password)
            except Exception as e:
                if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
                    print("Invalid API url", file=sys.stderr)
                    exit(1)
                raise
        else:
            raise

    if args.subparser_name == 'method':
        return json.dumps(rpc(zapi, args.method, args.arguments), indent=2)
    elif args.subparser_name == 'automator':
        automator(zapi, args)


def automator(zapi, args):
    """Automator subcommand"""
    automator = ZAutomator(rpc(zapi))
    action = args.action
    getattr(automator, action)(args.object, args.id)


def rpc(*args):
    """rpc works as a function generator or as the normal rpc method"""
    if len(args) == 2:
        raise TypeError('rpc must be pre initialized with the zapi or '
                        'called with all 3 args at once: '
                        'rpc(zapi, rpc_method, query_opts)')

    if len(args) == 1 or len(args) == 3:
        zapi = args[0]

    if len(args) != 3 and len(args) != 1:
        raise TypeError('rpc expect 1 or 3 arguments %s given' % len(args))

    def rpc(rpc_method, args):
        if '.' in rpc_method:
            method_arr = rpc_method.split('.')
        else:
            raise ValueError('Invalid RPC syntax should be object.action')
        args_arr = args
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

    if len(args) == 3:
        return rpc(*args[1:])
    else:
        return rpc
