#
# Copyright (c) 2008 rPath Inc.
#

import os
import string
import socket
import pwd, grp
import commands
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'condor'

    def configure(self):
        """
        [condor]
        # master host name
        condor_master = <FQDN>
        # shared secret key
        condor_secret = <string>
        #----------------------#
        # host name
        hostname = <FQDN>
        # collector name
        collector_name = CernVM
        # condor user
        condor_user = condor
        # condor group
        condor_group = condor
        # condor directory
        condor_dir = ~condor/condor
        # condor admin
        condor_admin = root@master
        highport = 9700
        lowport = 9600
        uid_domain = <hostname>
        filesystem_domain = <hostname>
        # allow_write = *.$uid_domain
        # localconfig = <filename>
        # slots = 1
        # slot_user = condor
        # cannonical_user = condor
        extra_vars =
        use_ips =
        """

        cfg = self.ud.getSection('condor')

        if 'hostname' in cfg:
            hostname = cfg['hostname']
            util.call(['hostname', hostname])

        # Array of lines of the condor_config.local file (will be rewritten)
        output = []

        # Dictionary of entries to go in the condor_config file (will be updated)
        condor_config_entries = {
            'NO_DNS': None,
            'DEFAULT_DOMAIN_NAME': None,
            'NETWORK_INTERFACE': None
        }

        output.append('# Generated using the CernVM amiconfig Condor plugin')

        #
        # We are now getting the assigned hostname (i.e., what this host thinks
        # its name is), the real hostname (the FQDN) and the IP address (the
        # one from which outbound connections are generated).
        #
        # This heuristics is needed to work around mismatches in the assigned
        # and real hostnames.
        #

        # Configured hostname
        assigned_hostname = socket.gethostname()
        output.append("# Assigned hostname: %s" % assigned_hostname)

        # IP address used for outbound connections. Using a dummy UDP
        # IPv4 socket to a known IP (not opening any actual connection)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect( ('8.8.8.8', 53) )
        real_ip = s.getsockname()[0]
        s.close()

        # Hostname obtained through reverse lookup from the IP
        #real_hostname = socket.gethostbyaddr(real_ip)[0]
        real_hostname = socket.getfqdn()
        output.append("# Real hostname: %s" % real_hostname)

        # Option to always use IP addresses
        use_ips = ('use_ips' in cfg) and (cfg['use_ips'] == 'true')
        if use_ips:
            output.append("# Always using IP addresses per user's choice")
            condor_config_entries['NO_DNS'] = 'True'
            condor_config_entries['DEFAULT_DOMAIN_NAME'] = 'virtual-analysis-facility'
            condor_config_entries['NETWORK_INTERFACE'] = real_ip

        condor_master = ""
        if 'condor_master' in cfg:
            # We are on a worker
            condor_master = cfg['condor_master']
            output.append('DAEMON_LIST = MASTER, STARTD')
        else:
            # We are on the Condor Master

            # If there's a mismatch between "real" and "assigned" hostname, use
            # the IP address
            if use_ips or (assigned_hostname != real_hostname):
                condor_master = real_ip
            else:
                condor_master = assigned_hostname

            output.append('DAEMON_LIST = COLLECTOR, MASTER, NEGOTIATOR, SCHEDD')

        condor_domain = real_hostname.partition('.')[2]
        if condor_domain == '':
            condor_domain = '*'

        output.append("CONDOR_HOST = %s" % (condor_master))
        if 'condor_admin' in cfg:
            output.append("CONDOR_ADMIN = %s" % (cfg['condor_admin']))
        else:
            output.append("CONDOR_ADMIN = root@%s" % (condor_master))
        if 'uid_domain' in cfg:
            if cfg['uid_domain'] == '*':
                output.append("")
                output.append("# Preserve UID of submitting user")
                output.append("UID_DOMAIN = *")
                output.append("TRUST_UID_DOMAIN = True")
                output.append("SOFT_UID_DOMAIN = True")
                output.append("")
            else:
                output.append("UID_DOMAIN = %s" % (cfg['uid_domain']))
        else:
            output.append("UID_DOMAIN = %s" % condor_domain)

        condor_user = 'condor'
        condor_group = 'condor'

        if 'condor_user' in cfg:
            condor_user = cfg['condor_user']
        if 'condor_group' in cfg:
            condor_group = cfg['condor_group']

        os.system("/usr/sbin/groupadd %s 2>/dev/null" % (condor_group))
        os.system("/usr/sbin/useradd -m -g %s %s > /dev/null 2>&1" % (condor_group, condor_user))
        os.system("/bin/chown -R %s:%s /var/lib/condor /var/log/condor /var/run/condor /var/lock/condor" % (condor_user, condor_group))

        condor_user_id = pwd.getpwnam(condor_user)[2]
        condor_group_id = grp.getgrnam(condor_group)[2]

        output.append("CONDOR_IDS = %s.%s" % (condor_user_id, condor_group_id))
        output.append("QUEUE_SUPER_USERS = root, %s" % (condor_user))

        condor_dir = pwd.getpwnam(condor_user)[5]
        if 'condor_dir' in cfg:
            condor_dir = cfg['condor_dir']
        os.system('mkdir -p ' + condor_dir + '/run/condor' + ' ' \
                              + condor_dir + '/log/condor' + ' ' \
                              + condor_dir + '/lock/condor' + ' ' \
                              + condor_dir + '/lib/condor/spool' + ' ' \
                              + condor_dir + '/lib/condor/execute')
        os.system("chown -R %s:%s %s" % (condor_user, condor_group, condor_dir))
        os.system("chmod 755 %s" % (condor_dir))
        output.append("LOCAL_DIR = %s" % (condor_dir))

        condor_highport = '9700'
        condor_lowport = '9600'
        if 'highport' in cfg:
            condor_highport = cfg['highport']
        if 'lowport' in cfg:
            condor_lowport = cfg['lowport']
        output.append("HIGHPORT = %s" % (condor_highport))
        output.append("LOWPORT = %s" % (condor_lowport))

        if 'collector_name' in cfg:
            output.append("COLLECTOR_NAME = %s" % (cfg['collector_name']))
        if 'allow_write' in cfg:
            output.append("ALLOW_WRITE = %s" % (cfg['allow_write']))

        #if 'localconfig' in cfg:
        #    output.append("CONFIG_CONDOR_LOCALCONFIG=%s" % (cfg['localconfig']))
        #if 'slots' in cfg:
        #    output.append("CONFIG_CONDOR_SLOTS=%s" % (cfg['slots']))
        #if 'slot_user' in cfg:
        #    output.append("CONFIG_CONDOR_SLOT_USER=%s" % (cfg['slot_user']))
        #if 'cannonical_user' in cfg:
        #    output.append("CONFIG_CONDOR_MAP=%s" % (cfg['cannonical_user']))

        if 'extra_vars' in cfg:
            output = output + cfg['extra_vars'].split(',');

        # Mangle the main condor_config configuration file
        conf_file_name = '/etc/condor/condor_config'
        conf_file_bak  = conf_file_name + '.0'
        try:
            os.rename( conf_file_name, conf_file_bak )
        except OSError as e:
            print "Cannot rename %s to %s: %s" % (conf_file_name, conf_file_bak, e)
            return

        try:
            fo = open(conf_file_name, 'a')
            fi = open(conf_file_bak, 'r')
            for line in fi:
                omit = False
                for key in condor_config_entries:
                    # Check for the equiv. of ^KEY[ \t=]
                    new_line = line.lstrip()
                    len_key = len(key)
                    next_char = new_line[len_key:len_key+1]
                    if new_line.startswith(key) and ( next_char == ' ' or next_char == '\t' or next_char == '=' ):
                       omit = True
                if omit == False:
                    fo.write( line.rstrip() + '\n' )
            for key,val in condor_config_entries.iteritems():
                if val is None:
                    break
                fo.write( "%s = %s\n" % (key, val) )
            fi.close()
            fo.close()
        except IOError as e:
            print "Error while modifying main configuration file: %s" % e
            return

        try:
            os.remove(conf_file_bak)
        except OSError as e:
            print "Cannot remove %s" % conf_file_bak
            # non-fatal

        # Write the condor_config.local configuration file
        if len(output):
            f = open('/etc/condor/condor_config.local', 'w')
            f.write('\n'.join(output))
            f.close()

            # Condor secret can be written only after creating the config file
            if 'condor_secret' in cfg:
                os.system("/usr/sbin/condor_store_cred add -c -p %s > /dev/null" % (cfg['condor_secret']))

            # We can start Condor now
            os.system("/sbin/chkconfig condor on")
            os.system("/sbin/service condor restart")
