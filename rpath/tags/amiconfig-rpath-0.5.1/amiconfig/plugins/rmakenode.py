#
# Copyright (c) 2007-2008 rPath, Inc.
#

import os

from amiconfig.errors import *
from rmakeplugin import rMakePlugin

class AMIConfigPlugin(rMakePlugin):
    name = 'rmakenode'

    def _write(self, file, value):
        fh = open(self.dir + os.sep + file, 'w')
        fh.write(value + '\n')
        fh.close()

    def pluginMethod(self):
        """
        buildDir /srv/rmake-builddir
        slots 8
        rmakeUrl https://build50.rdu.rpath.com:9999
        loadThreshold 10
        """

        noded = '/etc/rmake/node.d'
        if not os.access(noded, os.W_OK):
            return
        self.dir = noded

        if 'builddir' in self.rmakecfg:
            value = 'buildDir %s' % self.rmakecfg['builddir']
            self._write('builddir', value)
        if 'slots' in self.rmakecfg:
            value = 'slots %s' % self.rmakecfg['slots']
            self._write('slots', value)
        if 'rmakeurl' in self.rmakecfg:
            value = 'rmakeUrl %s' % self.rmakecfg['rmakeurl']
            self._write('rmakeurl', value)
        if 'loadthreashold' in self.rmakecfg:
            value = 'loadThreshold %s' % self.rmakecfg['loadthreashold']
            self._write('loadthreashold', value)
        if 'usecache' in self.rmakecfg:
            value = 'useCache %s' % self.rmakecfg['usecache']
            self._write('usecache', value)
