#
# Copyright (c) 2007-2008 rPath, Inc.
#

from amiconfig.lib import util
from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'raprsakey'

    def pluginMethod(self):
        if ('rappublickey' not in self.rpathcfg or
            'rapprivatekey' not in self.rpathcfg):
            return

        puburl = self.rpathcfg['rappublickey']
        privurl = self.rpathcfg['rapprivatekey']

        util.urlgrab(puburl, filename='/etc/raa/raa-service.pubkey')
        util.urlgrab(privurl, filename='/etc/raa/raa-service.privkey')
