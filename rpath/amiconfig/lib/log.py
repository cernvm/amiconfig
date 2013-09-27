#
# Copyright (c) 2008 rPath, Inc.
#

"""
Logging/syslog compat logger
"""

import syslog

syslog.openlog('amiconfig')

def _log(*args, **kwargs):
    syslog.syslog(*args, **kwargs)

warn = _log
info = _log
error = _log
critical = _log
