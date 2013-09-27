#
# Copyright (c) 2009 rPath, Inc.
#

"""
Plugin to disable ssh password auth by default. To disable this plugin pass in
disabled_plugins = disablesshpasswdauth in the amiconfig section of your
userdata.
"""

import os
import re
import tempfile

from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'disablesshpasswdauth'

    def configure(self):
        conffn = '/etc/ssh/sshd_config'

        tmpfd, tmpfn = tempfile.mkstemp()
        tmpfh = os.fdopen(tmpfd, 'w')

        regex = re.compile('.*PasswordAuthentication (yes|no).*')

        # Reconfigure to disable password auth.
        replaced = False
        for line in open(conffn):
            if regex.match(line):
                # Only replace the first instance of config.
                if not replaced:
                    tmpfh.write('PasswordAuthentication no\n')
                    replaced = True
                # Comment out other instances.
                else:
                    tmpfh.write('# %s' % line)
            else:
                tmpfh.write(line)

        tmpfh.close()
        os.rename(tmpfn, conffn)
