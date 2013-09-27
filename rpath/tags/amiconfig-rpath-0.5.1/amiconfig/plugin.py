#
# Copyright (c) 2007 rPath, Inc.
#

class AMIPlugin(object):
    name = None

    def __init__(self, id, ud):
        self.id = id
        self.ud = ud

    # Method for plugins to implement.
    def configure(self):
        pass
