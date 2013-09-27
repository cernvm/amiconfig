#
# Copyright (c) 2007-2008 rPath, Inc.
#

from amiconfig.lib import util
from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'rapcert'

    def pluginMethod(self):
        if 'rapcert' not in self.rpathcfg:
            return

        url = self.rpathcfg['rapcert']
        util.urlgrab(url, filename='/etc/ssl/pem/raa.pem')
