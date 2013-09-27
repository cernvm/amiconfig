#
# Copyright (c) 2008 rPath Inc.
#

import os
import math

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.lib import spacedaemon
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'storage'

    def configure(self):
        """
        [storage]
        # disable the spacedaemon
        daemon = False
        # size in GB
        pre-allocated-space = 20
        # list of ':' seperated dirs
        relocate-paths = /srv/rmake-builddir:/srv/mysql
        """

        try:
            blkdevmap = self.id.getBlockDeviceMapping()
        except EC2DataRetrievalError:
            return

        cfg = self.ud.getSection('storage')

        # Always mount swap
        if 'swap' in blkdevmap:
            swap = blkdevmap['swap']
            util.call(['swapon', swap])

        ephemeralDevs = []
        for key, dev in blkdevmap.iteritems():
            if 'ephemeral' in key:
                mntpnt = '/ephemeral/%s' % key[9:]
                ephemeralDevs.append(('/dev/%s' % dev, mntpnt))

        relocatePaths = []
        if 'relocate-paths' in cfg:
            relocatePaths = cfg['relocate-paths'].split(':')

        ephemeralDevsCount = len(ephemeralDevs)
        relocatePathsCount = len(relocatePaths)

        if ephemeralDevsCount < 1:
            return

        pathsPerDev = relocatePathsCount
        if ephemeralDevsCount > 1 and relocatePathsCount > 1:
            pathsPerDev = math.ceil(relocatePathsCount /
                                    float(ephemeralDevsCount))

        # The ephemeral space is a sparse file on an independent spindle. To
        # increase performance you want to create a file under the ephemeral
        # mout point to pre allocate the sparse file.
        size = 0
        if 'pre-allocated-space' in cfg:
            # size is in GB
            size = int(cfg['pre-allocated-space'])

        # Get daemon configuration.
        daemon = True
        if 'daemon' in cfg:
            daemon = bool(cfg['daemon'])

        paths = []
        for i, (dev, mntpnt) in enumerate(ephemeralDevs):
            util.mkdirChain(mntpnt)
            util.call(['mount', dev, mntpnt])

            if daemon:
                paths.append(mntpnt)
            else:
                fh = util.createUnlinkedTmpFile(mntpnt)
                util.growFile(fh, size * 1024)
                fh.close()

            for j in range((i+1) * pathsPerDev):
                if relocatePathsCount > j and os.path.exists(relocatePaths[j]) \
                    and not os.path.islink(relocatePaths[j]):
                    util.movetree(relocatePaths[j],
                                  '%s/%s' % (mntpnt, relocatePaths[j]))
                    os.symlink('%s/%s' % (mntpnt, relocatePaths[j]),
                               relocatePaths[j])

        if daemon and len(paths) > 0:
            exe = spacedaemon.__file__
            if exe.endswith('.pyc'):
                exe = exe[:-1]
            cmd = [ exe, str(size * 1024) ]
            cmd.extend(paths)
            util.call(cmd)
