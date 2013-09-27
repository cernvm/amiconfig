#
# Copyright (c) 2007 rPath, Inc.
#

import os
from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'rootsshkeys'

    def configure(self):
        try:
            key = self.id.getSSHKey()
        except EC2DataRetrievalError:
            # no key available
            return

        sshkeydir = '/root/.ssh/'
        sshdirperms = 0700
        # make ssh directory if it doesn't exist
        if not os.path.exists(sshkeydir):
            os.mkdir(sshkeydir)
            os.chmod(sshkeydir, sshdirperms)


        # ensure that key is not already in the authorized_keys file
        authkeysfile = '%s/authorized_keys' % sshkeydir
        if (not os.path.exists(authkeysfile) or 
            key not in open(authkeysfile).readlines()):
            # write the key to authorized_keys
            fh = open(authkeysfile, 'a')
            fh.write(key)
            fh.close()
