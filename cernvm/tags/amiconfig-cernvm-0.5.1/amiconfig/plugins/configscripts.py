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
    name = 'configscripts'

    def configure(self):
        """
        [configscripts]
        bundle= <string>
        """

        cfg = self.ud.getSection('configscripts')
        if 'bundle' in cfg:
            util.call(['/usr/sbin/amiconfig-helper',
                       '-b',
                       cfg['archive'],
                       '/etc/sysconfig/xrootd',
                       '/etc/xrootd/*',
                       '/etc/init.d/xrootd',
                       '/etc/init.d/cmsd',
                       '/etc/sysconfig/condor', 
                       '/etc/condor/*',
                       '/etc/gmond.conf',
                       '/etc/gmetad.conf',
                      ])
