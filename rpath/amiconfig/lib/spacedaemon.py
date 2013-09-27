#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

import os
import time
from syslog import syslog as log

from amiconfig.lib import util
from amiconfig.lib.daemon import Daemon

class SpaceAllocator(object):
    def __init__(self, path):
        self._path = path
        self._allocated = 0

    def _getFileSystemUsage(self):
        """ Returns disk usage on self._path in MB """
        fs = os.statvfs(self._path)
        blocksUsed = fs.f_blocks - fs.f_bfree
        sizeUsed = blocksUsed * fs.f_bsize / 1024 / 1024
        return sizeUsed

    def grow(self, size):
        # size is in MB
        # make sure that 20% over current usage is preallocated
        fh = util.createUnlinkedTmpFile(self._path)
        usage = self._getFileSystemUsage()
        while self._allocated < 1.2 * usage:
            util.growFile(fh, size)
            self._allocated += size
            log('growing %s to %sMB' % (self._path, self._allocated))
        fh.close()


class SpaceDaemon(Daemon):
    def __init__(self, paths, size):
        self._paths = paths
        self._size = int(size)
        self._fs = []
        for path in self._paths:
            self._fs.append(SpaceAllocator(path))

    def start(self):
        """ Every 5min try to allocate more space. """
        # Wait a couple of minutes before starting allocation to let the
        # machine finish booting.
        log('sleeping 120s before growing filesystems')
        time.sleep(120)
        while True:
            for fs in self._fs:
                fs.grow(self._size)
            log('sleeping 300s')
            time.sleep(300)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print "usage: %s <size in MB> <path, path, ...>" % sys.argv[0]
        sys.exit(1)

    size = sys.argv[1]
    paths = sys.argv[2:]

    d = SpaceDaemon(paths, size)
    sys.exit(d.daemonize())
