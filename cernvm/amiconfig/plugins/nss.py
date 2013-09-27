#
# Copyright (c) 2008 rPath Inc.
#

import os
import string
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'nss'

    def configure(self):
        """
        [nss]
        password = files
        group = files
        shadow = files
        hosts = files
        bootparams = nisplus [NOTFOUND=return] files
        ethers = files
        netmasks = files
        networks = files
        protocols = files
        rpc = files
        services = files
        netgroup = nisplus
        publickey =  nisplus
        automount = files nisplus
        aliases = files nisplus
        """

        cfg = self.ud.getSection('nss')
        for key in (   'passwd',
                       'group',
                       'shadow',
                       'hosts',
                       'bootparams',
                       'ethers',
                       'netmasks',
                       'networks',
                       'protocols',
                       'rpc',
                       'services',
                       'netgroup',
                       'publickey',
                       'automount',
                       'aliases'):
            if key in cfg:
                util.call(['/usr/sbin/amiconfig-helper',
                           '-f',
                           '/etc/nsswitch.conf',
                           '%s:=%s' % (key,cfg[key])])

