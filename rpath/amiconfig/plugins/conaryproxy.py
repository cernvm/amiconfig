#
# Copyright (c) 2007 rPath, Inc.
#

from amiconfig.errors import *
from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'conaryproxy'

    def pluginMethod(self):
        if 'conaryproxy' not in self.rpathcfg:
            return

        proxy = self.rpathcfg['conaryproxy']

        fh = open('/etc/conary/config.d/amiconfig', 'a')
        fh.write('conaryProxy http %s\n' % proxy)
        fh.write('conaryProxy https %s\n' % proxy.replace('http', 'https'))
        fh.close()
