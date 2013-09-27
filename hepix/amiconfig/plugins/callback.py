import os
import string
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'callback'
    
    def configure(self):
        """
        [callback]
        # ec2 stuff for call back
        # should only work with ssl access 
        EC2_URL = <string>
        EC2_SECRET_KEY = <string>
        EC2_ACCESS_KEY = <string>
        """
        
        cfg = self.ud.getSection('callback')

        output = []
        if 'ec2_url' in cfg:
            output.append("EC2_URL=%s" % (cfg['ec2_url']))
        if 'ec2_secret_key' in cfg:
            output.append("EC2_SECRET_KEY=%s" % (cfg['ec2_secret_key']))
        if 'ec2_access_key' in cfg:
            output.append("EC2_ACCESS_KEY=%s" % (cfg['ec2_access_key']))

        f = open('/etc/ec2.conf','w')
        f.write('\n'.join(output))
        f.close()
        os.system("chmod 400 /etc/ec2.conf")
