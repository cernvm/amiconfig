#
# Copyright (c) 2008 rPath, Inc.
#

import sys
import dns.query
import dns.update
import dns.tsigkeyring

from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin
from amiconfig.constants import version
from amiconfig.instancedata import InstanceData

class AMIConfigPlugin(AMIPlugin):
    name = 'dnsupdate'
    def configure(self):
        cfg = self.ud.getSection('dnsupdate')
        for key in ('tsighost', 'tsigkey', 'host', 'domain', 'server'):
            if key not in cfg:
                return

        instanceid = self.id.getInstanceId()
        ipaddr = self.id.getPublicIPv4()

        template = True
        for key in ('prefix', 'domain', 'start'):
            if key not in cfg:
                template = False
                break

        if template:
            index = int(self.id.getAMILaunchIndex())
            start = int(cfg['start'])
            clusterid = '%02d' % (start + index)
            cfg['host'] = '%s%s' % (cfg['prefix'], clusterid)

        # Set keyring using TSIG variables from User Data
        keyring = dns.tsigkeyring.from_text({
            cfg['tsighost'] : cfg['tsigkey']
        })
        update = dns.update.Update(cfg['domain'], keyring=keyring)

        # Clear all TXT and A entries for domain
        update.delete(cfg['host'], 'a')
        response = dns.query.tcp(update, cfg['server'])
        update.delete(cfg['host'], 'txt')
        response = dns.query.tcp(update, cfg['server'])

        # Create A entry with public IP address
        update.add(cfg['host'], 300, 'a', ipaddr)
        response = dns.query.tcp(update, cfg['server'])

        # Create TXT entry with instanceID
        update.add(cfg['host'], 300, 'txt', instanceid)
        response = dns.query.tcp(update, cfg['server'])

        # Response checking code should live here

        ret = 0
