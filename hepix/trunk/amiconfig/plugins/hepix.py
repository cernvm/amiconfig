import os
import string
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'hepix'
    
    def configure(self):
        """
        [hepix]
        # contextualization tar ball name
        context = <string>
        requiressl = <string>
        """
        
        cfg = self.ud.getSection('hepix')
        if 'context' in cfg:
            tarname = cfg['context']
        else:
            tarname = 'default.tgz'
        
        if 'requiressl' in cfg:
            requiressl = cfg['requiressl']
        else:
            requiressl = 'no'

        util.call(['/usr/sbin/site_context',tarname,requiressl])
