import os
import string
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'appliance'

    def configure(self):
        """
        [rpath]
        # Called rpath for historical reasons
        rap-password=password
        """

        cfg = self.ud.getSection('rpath')
        
        if 'rap-password' in cfg:
          util.call(['htpasswd', '-mb', "/usr/libexec/cernvm-appliance-agent/.htpasswd %s" % (cfg['rap-password'])])
          util.call(['mkdir', '-p', '/var/lib/cernvm-appliance-agent'])
          util.call(['touch', '/var/lib/cernvm-appliance-agent/password_set'])
          util.call(['chown', '-R', 'cernvm-appliance-agent', '/var/lib/cernvm-appliance-agent'])
          util.call(['/sbin/service', 'cernvm-appliance-agent', 'restart'])
