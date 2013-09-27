#
# Copyright (c) 2007 rPath, Inc.
#

from amiconfig.plugin import AMIPlugin

class rPathPlugin(AMIPlugin):
    def configure(self):
        self.rpathcfg = self.ud.getSection('rpath')
        if self.rpathcfg:
            self.pluginMethod()
