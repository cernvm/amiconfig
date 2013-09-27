#
# Copyright (c) 2008 rPath, Inc.
#

import os

from rmakeplugin import rMakePlugin

class AMIConfigPlugin(rMakePlugin):
    name = 'rmakeserver'

    def pluginMethod(self):
        self._setupProxy()
        self._setuprBuilder()
        self._setupRepoUrl()

    def _setupProxy(self):
        proxycfg = '/etc/rmake/server.d/proxy'

        if 'conaryproxy' in self.rmakecfg:
            proxy = self.rmakecfg['conaryproxy']
        else:
            proxy = 'http://%s:7778/' % self.id.getLocalHostname()

        fh = open(proxycfg, 'w')
        fh.write('proxy %s\n' % proxy)

    def _setuprBuilder(self):
        rbuildercfg = '/etc/rmake/server.d/rbuilder'

        if 'rbuilderurl' in self.rmakecfg:
            fh = open(rbuildercfg, 'w')
            fh.write('rbuilderUrl %s\n' % self.rmakecfg['rbuilderurl'])

    def _setupRepoUrl(self):
        repourlcfg = '/etc/rmake/server.d/serverurl'

        if 'serverurl' in self.rmakecfg:
            url = self.rmakecfg['serverurl']
        else:
            url = 'http://%s/conary/' % self.id.getLocalHostname()

        fh = open(repourlcfg, 'w')
        fh.write('serverUrl %s\n' % url)
