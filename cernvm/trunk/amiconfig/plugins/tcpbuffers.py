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
    name = 'tcpbuffers'

    def configure(self):
        """
        [tcpbuffers]
        # increase TCP max buffer size setable using setsockopt()
        # 16 MB with a few parallel streams is recommended for most 10G paths
        # 32 MB might be needed for some very long end-to-end 10G or 40G paths
        net.core.rmem_max = 16777216
        net.core.wmem_max = 16777216
        # increase Linux autotuning TCP buffer limits
        # min, default, and max number of bytes to use
        # (only change the 3rd value, and make it 16 MB or more)
        net.ipv4.tcp_rmem = 4096 87380 16777216
        net.ipv4.tcp_wmem = 4096 65536 16777216
        # recommended to increase this for 10G NICS
        net.core.netdev_max_backlog = 30000
        # these should be the default, but just to be sure
        net.ipv4.tcp_timestamps = 1
        net.ipv4.tcp_sack = 1
        """

        cfg = self.ud.getSection('tcpbuffers')
        
        for var in [ 'net.core.rmem_max', 'net.core.wmem_max', 'net.ipv4.tcp_rmem', 'net.ipv4.tcp_wmem', 'net.core.netdev_max_backlog', 'net.ipv4.tcp_timestamps', 'net.ipv4.tcp_sack'  ]:
            if var in cfg:
                util.call(['/sbin/sysctl', '-w',"%s=%s" % (var,cfg['var'])])

                            
