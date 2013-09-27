#
# Copyright (c) 2007-2008 rPath, Inc.
#

import urllib
import urlparse

from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'noip'

    def configure(self):
        cfg = self.ud.getSection('noip')

        for key in ('username', 'password'):
            if key not in cfg:
                return

        template = True
        for key in ('prefix', 'domain', 'start'):
            if key not in cfg:
                template = False
                break

        if not template and 'hostname' not in cfg:
            return

        if template:
            index = int(self.id.getAMILaunchIndex())
            start = int(cfg['start'])
            id = '%02d' % (start + index)
            cfg['hostname'] = '%s%s.%s' % (cfg['prefix'], id, cfg['domain'])

        url = ('https://%(username)s:%(password)s@dynupdate.no-ip.com'
               '/nic/update?hostname=%(hostname)s') % cfg

        urlfh = urllib.urlopen(url)

        ret = urlfh.read()
