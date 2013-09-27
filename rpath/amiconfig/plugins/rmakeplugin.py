#
# Copyright (c) 2007 rPath, Inc.
#

from amiconfig.plugin import AMIPlugin

class rMakePlugin(AMIPlugin):
    def configure(self):
        self.rmakecfg = self.ud.getSection('rmake')
        if self.rmakecfg:
            self.pluginMethod()
