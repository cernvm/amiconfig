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
    name = 'condor'

    def configure(self):
        """
        [condor]
        # master host name
        condor_master = <FQDN>
        # shared secret key
        condor_secret = <string>
        #----------------------#
        # host name
        hostname = <FQDN>
        # collector name
        collector_name = CernVM
        # condor user
        condor_user = condor
        # condor group
        condor_group = condor
        # condor directory
        condor_dir = ~condor/condor
        # condor admin
        condor_admin = root@master
        highport = 9700
        lowport = 9600
        uid_domain = <hostname>
        filesystem_domain = <hostname>
        allow_write = *.$uid_domain
        localconfig = <filename>
        slots = 1
        slot_user = condor
        cannonical_user = condor
        extra_vars = 
        """

        cfg = self.ud.getSection('condor')

        if 'hostname' in cfg:
            hostname = cfg['hostname']
            util.call(['hostname', hostname])

        output = []

        if 'condor_master' in cfg:
            output.append("CONFIG_CONDOR_MASTER=%s" % (cfg['condor_master']))
        if 'condor_secret' in cfg:
            output.append("CONFIG_CONDOR_SECRET=%s" % (cfg['condor_secret']))
        if 'collector_name' in cfg:
            output.append("CONFIG_COLLECTOR_NAME=%s" % (cfg['collector_name']))
        if 'condor_user' in cfg:
            output.append("CONFIG_CONDOR_USER=%s" % (cfg['condor_user']))
        if 'condor_group' in cfg:
            output.append("CONFIG_CONDOR_GROUP=%s" % (cfg['condor_group']))
        if 'condor_dir' in cfg:
            output.append("CONFIG_CONDOR_DIR=%s" % (cfg['condor_dir']))
        if 'condor_admin' in cfg:
            output.append("CONFIG_CONDOR_ADMIN=%s" % (cfg['condor_admin']))
        if 'highport' in cfg:
            output.append("CONFIG_CONDOR_HIGHPORT=%s" % (cfg['highport']))
        if 'lowport' in cfg:
            output.append("CONFIG_CONDOR_LOWPORT=%s" % (cfg['lowport']))
        if 'uid_domain' in cfg:
            output.append("CONFIG_CONDOR_UID_DOMAIN=%s" % (cfg['uid_domain']))
        if 'allow_write' in cfg:
            output.append("CONFIG_CONDOR_ALLOW_WRITE=%s" % (cfg['allow_write']))
        if 'localconfig' in cfg:
            output.append("CONFIG_CONDOR_LOCALCONFIG=%s" % (cfg['localconfig']))
        if 'slots' in cfg:
            output.append("CONFIG_CONDOR_SLOTS=%s" % (cfg['slots']))
        if 'slot_user' in cfg:
            output.append("CONFIG_CONDOR_SLOT_USER=%s" % (cfg['slot_user']))
        if 'cannonical_user' in cfg:
            output.append("CONFIG_CONDOR_MAP=%s" % (cfg['cannonical_user']))

        if 'extra_vars' in cfg:
            output.append("CONFIG_CONDOR_EXTRA_VARS=%s" % (cfg['extra_vars']))

        if len(output): 
            f = open('/etc/sysconfig/condor','w')
            f.write('\n'.join(output))
            f.close()
            os.system("chmod 400 /etc/sysconfig/condor")
            os.system("/sbin/service condor start")
            
