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
    name = 'squid'

    def configure(self):
        """
        [squid]
        cvmfs_server = cernvm-webfs.cern.ch
        cache_mem = 4096 MB
        maximum_object_size_in_memory =  32 KB
        cache_dir = /var/spool/squid
        cache_dir_size = 50000
        """

        cfg = self.ud.getSection('squid')

        expr=['sed']

        cvmfs_server = 'cernvm-webfs.cern.ch'
        if 'cvmfs_server' in cfg:
            cvmfs_server = cfg['cvmfs_server']
        expr.append('-e')
        expr.append('s/@cvmfs_server@/%s/g' % cvmfs_server)

        cache_mem = '4096 MB'
        if 'cache_mem' in cfg:
            cache_mem = cfg['cache_mem']
        expr.append('-e')
        expr.append('s/@cache_mem@/%s/g' % cache_mem)

        maximum_object_size_in_memory = '32 KB'
        if 'maximum_object_size_in_memory' in cfg:
            maximum_object_size_in_memory = cfg['maximum_object_size_in_memory']
        expr.append('-e')
        expr.append('s/@maximum_object_size_in_memory@/%s/g' % maximum_object_size_in_memory)

        cache_dir = '/var/spool/squid'
        if 'cache_dir' in cfg:
            cache_dir = cfg['cache_dir']
        expr.append('-e')
        expr.append('s/@cache_dir@/%s/g' % cache_dir)

        cache_dir_size = '50000'
        if 'cache_dir_size' in cfg:
            cache_dir_size = cfg['cache_dir_size']
        expr.append('-e')
        expr.append('s/@cache_dir_size@/%s/g' % cache_dir_size)

        expr.append('/etc/squid/squid.conf.cernvm')
        expr.append('>')
        expr.append('/etc/squid/squid.conf')
        
        os.system(' '.join(expr))


