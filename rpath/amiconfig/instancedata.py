#
# Copyright (c) 2007-2008 rPath, Inc.
#

import socket
import urllib
import os

from amiconfig import metadataservice
from amiconfig.errors import *
from amiconfig.constants import version

class URLOpener(urllib.FancyURLopener):
    version = 'AMIConfig/%s elliot@rpath.com' % version

urllib._urlopener = URLOpener()


class InstanceData:
    apiversion = metadataservice.MetadataService.APIVERSION

    def __init__(self):
       context_url = os.getenv("AMICONFIG_CONTEXT_URL")
       if context_url is not None:
           self.urlbase = context_url
       else:
           self.urlbase = 'http://%s/%s' % (metadataservice.MetadataService.SERVICE_IP, self.apiversion)

    def open(self, path):
        try:
            results = urllib.urlopen('%s/%s' % (self.urlbase,
                                                   path))
        except Exception, e:
            raise EC2DataRetrievalError, '[Errno %s] %s' % (e.errno, e.strerror)
        if results.headers.gettype() == 'text/html':
            # Eucalyptus returns text/html and no Server: header
            # We want to protect ourselves from HTTP servers returning real
            # HTML, so let's hope at least they're conformant and return a
            # Server: header
            if 'server' in results.headers:
                raise EC2DataRetrievalError, '%s' % results.read()
        return results

    def read(self, path):
        ec2_user_data_url = os.getenv("AMICONFIG_EC2_USER_DATA_URL")
        if ec2_user_data_url is not None:
            try:
                results = urllib.urlopen('%s/user-data' % (ec2_user_data_url))
            except Exception, e:
                raise EC2DataRetrievalError, '[Errno %s] %s' % (e.errno, e.strerror)
            if results.headers.gettype() == 'text/html':
                # Eucalyptus returns text/html and no Server: header
                # We want to protect ourselves from HTTP servers returning real
                # HTML, so let's hope at least they're conformant and return a
                # Server: header
                if 'server' in results.headers:
                    raise EC2DataRetrievalError, '%s' % results.read()
            return results.read()
        return self.open(path).read()

    def getUserData(self):
        return self.read('user-data')

    def getAMIId(self):
        return self.read('meta-data/ami-id')

    def getAMILaunchIndex(self):
        return self.read('meta-data/ami-launch-index')

    def getAMIManifestPath(self):
        return self.read('meta-data/ami-manifest-path')

    def getInstanceId(self):
        return self.read('meta-data/instance-id')

    def getInstanceType(self):
        return self.read('meta-data/instance-type')

    def getLocalHostname(self):
        return self.read('meta-data/local-hostname')

    def getLocalIPv4(self):
        return self.read('meta-data/local-ipv4')

    def getPublicHostname(self):
        return self.read('meta-data/public-hostname')

    def getPublicIPv4(self):
        return self.read('meta-data/public-ipv4')

    def getReservationId(self):
        return self.read('meta-data/reservation-id')

    def getSecurityGroups(self):
        list = []
        for group in self.open('meta-data/security-groups'):
            list.append(group.strip())
        return list

    def getKeyIdList(self):
        list = []
        for key in self.open('meta-data/public-keys/'):
            lst = key.split('=')
            if len(lst) in [0, 1]:
                continue
            id = lst[0]
            name = '='.join(lst[1:])
            list.append((id, name))
        return list

    def getSSHKey(self, id=0):
        return self.read('meta-data/public-keys/%s/openssh-key' % id)

    def getBlockDeviceMapping(self):
        map = {}
        for key in self.read('meta-data/block-device-mapping/').split():
            map[key] = self.read('meta-data/block-device-mapping/%s' % key)
        return map
