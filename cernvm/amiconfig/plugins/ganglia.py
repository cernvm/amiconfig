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
    name = 'ganglia'

    def configure(self):
        """
        [ganglia]
        name = CernVM
        owner = unknown
        latlong = unknown
        url = unkonown
        location = unknown
        host = localhost
        -------------------
        bind_hostname = yes
        port = 8649
        ttl = 1
        """

        cfg = self.ud.getSection('ganglia')

        expr=['sed']

        name = 'CernVM'
        if 'name' in cfg:
            name = cfg['name']
        expr.append('-e')
        expr.append('s/@name@/%s/g' % name)

        owner = 'unknown'
        if 'owner' in cfg:
            owner = cfg['owner']
        expr.append('-e')
        expr.append('s/@owner@/%s/g' % owner)

        latlong = 'unknown'
        if 'latlong' in cfg:
            latlong = cfg['latlong']
        expr.append('-e')
        expr.append('s/@latlong@/%s/g' % latlong)

        url = 'unknown'
        if 'url' in cfg:
            url = cfg['url']
        expr.append('-e')
        expr.append('s/@url@/%s/g' % url)

        location = 'unknown'
        if 'location' in cfg:
            location = cfg['location']
        expr.append('-e')
        expr.append('s/@location@/%s/g' % location)

        host = 'localhost'
        if 'host' in cfg:
            host = cfg['host']
        expr.append('-e')
        expr.append('s/@host@/%s/g' % host)

        bind_hostname = 'yes'
        if 'bind_hostname' in cfg:
            bind_hostname = cfg['bind_hostname']
        expr.append('-e')
        expr.append('s/@bind_hostname@/%s/g' % bind_hostname)

        port = '8649'
        if 'port' in cfg:
            port = cfg['port']
        expr.append('-e')
        expr.append('s/@port@/%s/g' % port)

        ttl = '1'
        if 'ttl' in cfg:
            ttl = cfg['ttl']
        expr.append('-e')
        expr.append('s/@ttl@/%s/g' % ttl)

        expr.append('/etc/gmond.conf.cernvm')
        expr.append('>')
        expr.append('/etc/gmond.conf')

        os.system(' '.join(expr))
                                        
