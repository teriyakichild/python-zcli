from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "zcli"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "0.1.0",
        author = "Tony Rogers",
        author_email = "tony.rogers@rackspace.com",
        url = "https://github.com/teriyakichild/python-zcli",
        license = 'internal use',
        packages = [NAME],
        package_dir = {NAME: NAME},
        description = "Zabbix CLI.",

        install_requires = ['requests',
                            'argparse',
                            'pyzabbix',
                            'ConfigParser'],
        entry_points={
            'console_scripts': [ 'zcli = zcli:cli' ],
        }
    )

