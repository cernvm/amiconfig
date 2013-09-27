#
# Copyright (c) 2008 rPath Inc.
#

import os
import string
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'puppet'

    def configure(self):
        """
        [puppet]
        # The puppetmaster server
        puppet_server=puppet
        #----------------------------------------------------------------------
        # If you wish to specify the port to connect to do so here
        puppet_port=8140
        # Where to log to. Specify syslog to send log messages to the system log.
        puppet_log=/var/log/puppet/puppet.log
        # You may specify other parameters to the puppet client here
        puppet_extra_opts=--waitforcert=500
        # Location of the main manifest
        puppetmaster_manifest=/etc/puppet/manifests/site.pp
        # Where to log general messages to.
        # Specify syslog to send log messages to the system log.
        puppetmaster_log=syslog
        # You may specify an alternate port or an array of ports on which
        # puppetmaster should listen. Default is: 8140
        # If you specify more than one port, the puppetmaster ist automatically
        # started with the servertype set to mongrel. This might be interesting
        # if you'd like to run your puppetmaster in a loadbalanced cluster.
        # Please note: this won't setup nor start any loadbalancer.
        # If you'd like to run puppetmaster with mongrel as servertype but only
        # on one (specified) port, you have to add --servertype=mongrel to
        # PUPPETMASTER_EXTRA_OPTS.
        # Default: Empty (Puppetmaster isn't started with mongrel, nor on a
        # specific port)
        # Please note: Due to reduced options in the rc-functions lib in RHEL/Centos
        # versions prior to 5, this feature won't work. Fedora versions >= 8 are
        # known to work.
        puppetmaster_ports=""
        # Puppetmaster on a different port, run with standard webrick servertype
        puppetmaster_ports="8141"
        # Example with multiple ports which will start puppetmaster with mongrel
        # as a servertype
        puppetmaster_ports=( 18140 18141 18142 18143 )
        # You may specify other parameters to the puppetmaster here
        puppetmaster_extra_opts=--no-ca
        """

        output = []
        if 'puppet_server' in cfg:
            config_file = '/etc/sysconfig/puppet'
            output.append("PUPPET_SERVER=%s" % (cfg['puppet_server']))
            if 'puppet_port' in cfg:
                output.append("PUPPET_PORT=%s" % (cfg['puppet_port']))
            if 'puppet_log' in cfg:
                output.append("PUPPET_LOG=%s" % (cfg['puppet_log']))
            if 'puppet_extra_opts' in cfg:
                output.append("PUPPET_EXTRA_OPTS=%s" % (cfg['puppet_extra_opts']))
        else:
            config_file = '/etc/sysconfig/puppetmaster'
            if 'puppetmaster_manifest' in cfg:
                output.append("PUPPETMASTER_MANIFEST=%s" % (cfg['puppetmaster_manifest']))
            if 'puppetmaster_ports' in cfg:
                output.append("PUPPETMASTER_PORTS=%s" % (cfg['puppetmaster_ports']))
            if 'puppetmaster_log' in cfg:
                output.append("PUPPETMASTER_LOG=%s" % (cfg['puppetmaster_log']))
            if 'puppetmaster_extra_opts' in cfg:
                output.append("PUPPETMASTER_EXTRA_OPTS=%s" % (cfg['puppetmaster_extra_opts']))

        if len(output) :
            f = open(config_file,'w')
            f.write('\n'.join(output))
            f.close()

            
