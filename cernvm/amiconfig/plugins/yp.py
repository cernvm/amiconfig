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
    name = 'yp'

    def configure(self):
        """
        [yp]
        ypserver  = hostname
        """

        cfg = self.ud.getSection('yp')

        if 'ypserver' in cfg:
            util.call(['/usr/sbin/amiconfig-helper',
                           '-f',
                           '/etc/yp.conf',
                           '%s=%s' % ('ypserver',cfg['ypserver'])])
            return 
        if 'server' in cfg and 'domain' in cfg:
            util.call(['/usr/sbin/amiconfig-helper',
                           '-f',
                           '/etc/yp.conf',
                           '%s="%s server %s"' % ('domain',cfg['domain'],cfg['server'])])
            return 
        if  'domain' in cfg:
            util.call(['/usr/sbin/amiconfig-helper',
                           '-f',
                           '/etc/yp.conf',
                           '%s="%s broadcast"' % ('domain',cfg['domain'])])
            return 
