#
# Copyright (c) 2011 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

import logging
import os
import subprocess
import urllib2
import socket

class MetadataService(object):
    APIVERSION = '2007-12-15'
    SERVICE_IP = '169.254.169.254'
    LOGGING_NAME = "amiconfig.metadataservice"

    def __init__(self, debug=False):
        logger = self.getLogger((debug and logging.DEBUG) or logging.WARN)
        self.setLogger(logger)

    def setLogger(self, logger):
        self.log = logger

    def canConnect(self):         
        if os.getenv("AMICONFIG_CONTEXT_URL") is not None:
            context_url = os.getenv("AMICONFIG_CONTEXT_URL")
            if context_url is not None:
                self.log.debug("Metadata service; context url [%s]; " % ( context_url ) )
                return True
        url = "http://%s/%s" % (self.SERVICE_IP, self.APIVERSION)
        try:
            dt = socket.getdefaulttimeout()
            socket.setdefaulttimeout(3)
            handle = urllib2.urlopen(url)
            socket.setdefaulttimeout(dt)
            ec2_index = handle.read()
            if ("user-data" in ec2_index) and ("meta-data" in ec2_index):
                return True
            else:
                self.log.debug("Didn't find proper ec2 index at %s" % url)
        except Exception, e:
            self.log.debug("While opening %s: %s" % (url, e))
        return False

    @classmethod
    def getLogger(cls, level):
        logger = logging.getLogger(cls.LOGGING_NAME)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
