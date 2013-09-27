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
    name = 'ldap'

    def configure(self):
        """
        [ldap]
        base = <dn>
        url  = <url>
        """

        cfg = self.ud.getSection('ldap')
        for key in ( 'base',
                     'url'):
            if key in cfg:
                util.call(['/usr/sbin/amiconfig-helper',
                           '-f',
                           '/etc/ldap.conf',
                           '%s=%s' % (key,cfg[key])])

