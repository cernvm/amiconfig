#
# Copyright (c) 2008 rPath Inc.
#

import os
import string
import socket
import pwd, grp
import commands
from random import choice
import multiprocessing

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'workqueue'

    def configure(self):
        """
        [workqueue]
        # master host name
        catalog_server = <FQDN>
        # shared secret key
        workqueue_project = <string>
        workqueue_user = workqueue
        """

        cfg = self.ud.getSection('workqueue')

        output = []

        if 'catalog_server' in cfg:
            output.append("CATALOG_SERVER=%s:9097" % (cfg['catalog_server']))
            if 'workqueue_project' in cfg:
                output.append("WQ_PROJECT=%s" % (cfg['workqueue_project']))
            if 'workqueue_user' in cfg:
                output.append("WQ_USER=%s" % (cfg['workqueue_user']))
            output.append("WQ_WORKERS=%s" % multiprocessing.cpu_count())
        else:
            output.append("START_CATALOG_SERVER=yes")

        if len(output):
            f = open('/etc/workqueue.local','w')
            f.write('\n'.join(output))
            f.close()
            os.system("/sbin/chkconfig --add workqueue")
            os.system("/sbin/service workqueue start")
