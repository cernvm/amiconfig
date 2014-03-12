#
# vaf-setup.py -- by Dario Berzano <dario.berzano@cern.ch>
#
# Plugin for amiconfig for configuring the Virtual Analysis Facility.
#
# See: https://github.com/dberzano/virtual-analysis-facility
#

import os
import pwd
import string
import time
import socket
import re
import subprocess

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin


class AMIConfigPlugin(AMIPlugin):

    # Name of this plugin
    name = 'vaf-setup'

    # Where is sshcertauth? Usually on cvmfs
    sshcertauth_src = '/cvmfs/sft.cern.ch/lcg/dev/cvmvaf/sshcertauth'

    # Where to install (i.e. symlink) sshcertauth
    sshcertauth_dst = '/var/www/html/auth'

    # Where to create the config file of sshcertauth
    sshcertauth_conf = '/etc/sshcertauth/conf.php'

    # Directory of the authorized public keys
    auth_keys_dir = '/etc/ssh/authorized_keys_globus'

    # The pool_users plugin requires a mapfile
    auth_mapfile = '/etc/sshcertauth-x509-map'

    # Base uid for pool accounts
    pool_base_uid = 50000

    # Pool group name
    pool_group = 'pool'

    # Pool group gid
    pool_gid = 50000

    # ALICE group name
    alice_group = 'alice'

    # ALICE group gid
    alice_gid = 1395

    # User of apache2 (httpd)
    httpd_user = 'apache'

    # Automatically generated configuration for httpd
    httpd_ssl_conf = '/etc/httpd/conf.d/ssl.conf'

    # Where to store the host certificate and private key
    ssl_dir = '/etc/grid-security'

    # Path of recognized CAs
    ssl_ca_path = '/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/etc/grid-security/certificates'
    #ssl_ca_path = /cvmfs/alice.cern.ch/x86_64-2.6-gnu-4.1.2/Packages/AliEn/v2-19/api/share/certificates

    # crontab file for purging expired keys
    cron_expiry = '/etc/cron.d/sshcertauth'

    # sshd configuration
    sshd_conf = '/etc/ssh/sshd_config'

    # The sudoers file
    sudoers = '/etc/sudoers'

    # Configuration for sssd
    sssd_conf = '/etc/sssd/sssd.conf'

    # Configuration for nscd
    nscd_conf = '/etc/nscd.conf'


    def configure(self):
        """
        [vaf-setup]
        client_settings=alice
        node_type=[master|slave]  # defaults to slave
        auth_method=[alice_ldap|pool_users|<none>]  # defaults to <none>
        num_pool_accounts=50  # mandatory if auth_method==pool_users
        """

        cfgraw = self.ud.getSection('vaf-setup')

        # Validate auth_method: abort on error
        if 'auth_method' in cfgraw:
            auth_method = cfgraw['auth_method']
            if auth_method == 'pool_users':
                if 'num_pool_accounts' in cfgraw:
                    try:
                        num_pool_accounts = int(cfgraw['num_pool_accounts'])
                        if num_pool_accounts <= 1:
                            raise ValueError('')
                    except ValueError as e:
                        # Fatal
                        print "Invalid number of pool accounts: %s" % cfgraw['num_pool_accounts']
                        return
                else:
                    # Fatal
                    print "No number of pool accounts specified"
                    return
            elif auth_method == 'alice_ldap':
                num_pool_accounts = 0  # unused
            else:
                # Fatal
                print "Unknown authentication method: %s" % auth_method
                return
        else:
            # No authentication method specified: don't config sshcertauth
            auth_method = None


        # On master and with some authentication method defined: sshcertauth
        if 'node_type' in cfgraw and cfgraw['node_type'] == 'master' and auth_method is not None:

            if self.config_sshcertauth(auth_method, num_pool_accounts) == False:
                return

        if auth_method == 'pool_users':
            if self.config_pool_users(num_pool_accounts) == False:
                return

        elif auth_method == 'alice_ldap':
            if self.config_alice_ldap() == False:
                return


    def config_sshcertauth(self, auth_method, num_pool_accounts):
        """Configures a lot of things for making sshcertauth work.
        """

        # Parent directory
        parent = os.path.dirname( self.sshcertauth_dst )
        if not os.path.isdir(parent):
            try:
                os.makedirs(parent, 0755)
            except OSError as e:
                pass

        # Symlink
        try:
            if os.path.islink( self.sshcertauth_dst ):
                os.unlink( self.sshcertauth_dst )
            os.symlink(self.sshcertauth_src, self.sshcertauth_dst)
        except OSError as e:
            print "Cannot create symbolic link %s: %s" % (self.sshcertauth_dst, e)
            return False

        # Create config file for sshcertauth
        parent = os.path.dirname(self.sshcertauth_conf)
        try:
            os.mkdir(parent, 0755)
        except OSError as e:
            pass

        try:
            f = open( self.sshcertauth_conf, 'w' )
            lines = [
                '<?php',
                '# Automatically generated by the vaf-setup plugin of amiconfig',
                '# Generated at %s' % (time.strftime('%Y-%m-%d %H:%M:%S %z')),
                '$$sshPort = 22;',
                '$$sshKeyDir = "${AUTH_KEYS_DIR}";',
                '$$maxValiditySecs = 43200;',
                '$$pluginUser = "${AUTH_METHOD}";',
                '$$opensslBin = "openssl";',
                '$$mapFile = "${AUTH_MAPFILE}";',
                '$$mapValiditySecs = 172800;',
                '$$mapIdLow = 1;',
                '$$mapIdHi = ${NUM_POOL_ACCOUNTS};',
                '$$mapUserFormat = "pool%03u";',
                '?>' ]
            for l in lines:
                f.write( string.Template(l).substitute({
                    'AUTH_KEYS_DIR': self.auth_keys_dir,
                    'AUTH_METHOD': auth_method,
                    'AUTH_MAPFILE': self.auth_mapfile,
                    'NUM_POOL_ACCOUNTS': num_pool_accounts
                }) )
                f.write('\n')
            f.close()

        except IOError as e:
            print "Cannot write configuration %s: %s" % (self.sshcertauth_conf, e)
            return False

        try:
            os.chown(self.sshcertauth_conf, 0, 0)
            os.chmod(self.sshcertauth_conf, 0644)
        except OSError as e:
            print "Cannot change permissions of %s: %s" % (self.sshcertauth_conf, e)
            return

        # Create the configuration file for apache2 (TODO: it is a little bit convoluted)
        try:
            f = open(self.httpd_ssl_conf, 'w')
            f.write( string.Template("""
LoadModule ssl_module modules/mod_ssl.so
Listen 443
AddType application/x-x509-ca-cert .crt
AddType application/x-pkcs7-crl .crl
SSLPassPhraseDialog builtin
SSLSessionCache shmcb:/var/cache/mod_ssl/scache(512000)
SSLSessionCacheTimeout 300
SSLMutex default
SSLRandomSeed startup file:/dev/urandom 256
SSLRandomSeed connect builtin
SSLCryptoDevice builtin
<VirtualHost _default_:443>
ErrorLog logs/ssl_error_log
TransferLog logs/ssl_access_log
LogLevel warn
SSLEngine on
SSLProtocol all -SSLv2
SSLCipherSuite ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW
<Files ~ "\.(cgi|shtml|phtml|php3?)$">
SSLOptions +StdEnvVars
</Files>
<Directory "/var/www/cgi-bin">
SSLOptions +StdEnvVars
</Directory>
SetEnvIf User-Agent ".*MSIE.*" \\
     nokeepalive ssl-unclean-shutdown \\
     downgrade-1.0 force-response-1.0
CustomLog logs/ssl_request_log \\
      "%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x \\"%r\\" %b"
### Customized for sshcertauth ###
SSLCertificateFile ${SSL_DIR}/hostcert.pem
SSLCertificateKeyFile ${SSL_DIR}/hostkey.pem
SSLCACertificatePath ${SSL_CA_PATH}
SSLVerifyDepth 10
<Directory ${SSHCERTAUTH_DST}>
SSLVerifyClient require
SSLOptions +StdEnvVars +ExportCertData
AllowOverride all
</Directory>
</VirtualHost>
"""
                ).safe_substitute({
                    'SSHCERTAUTH_DST': self.sshcertauth_dst,
                    'SSL_DIR': self.ssl_dir,
                    'SSL_CA_PATH': self.ssl_ca_path
                }) )

            f.close()
        except IOError as e:
            print 'Cannot write %s: %s' % (self.httpd_ssl_conf, e)

        # Create a new self-signed certificate if necessary
        if not os.path.isfile(self.ssl_dir+'/hostcert.pem') or not os.path.isfile(self.ssl_dir+'/hostkey.pem'):

            try:
                os.mkdir(self.ssl_dir, 0755)
            except OSError:
                pass

            my_ipv4 = self.get_ipv4()

            openssl_cmd = 'openssl req -new -newkey rsa:2048 -days 365 -nodes -x509'.split(' ')
            openssl_cmd.extend([ '-subj', '/CN='+my_ipv4 ])
            openssl_cmd.extend([ '-keyout', self.ssl_dir+'/hostkey.pem'])
            openssl_cmd.extend([ '-out', self.ssl_dir+'/hostcert.pem'])

            try:
                r = subprocess.call(openssl_cmd)
            except OSError as e:
                print "Cannot invoke openssl: %s" % e
                return False

            if r != 0:
                print "Error generating certificate and keys: %d" % r
                return False

        try:
            os.chmod(self.ssl_dir + '/hostcert.pem', 0444)
            os.chmod(self.ssl_dir + '/hostkey.pem', 0400)
        except OSError:
            print 'Cannot change mode of certificate/key'
            return False

        # Enable keys expiration (via crontab)
        try:
            f = open(self.cron_expiry, 'w')
            f.write('*/5 * * * * root %s/keys_keeper.sh expiry\n' % self.sshcertauth_dst)
            f.close()
        except IOError as e:
            print 'Cannot write %s: %s' % (self.cron_expiry, e)

        # Authorized keys path for SSH
        try:
            os.mkdir(self.auth_keys_dir)
            # Preserve authorized keys for root
            root_key = '/root/.ssh/authorized_keys'
            if os.path.isfile(root_key):
                os.symlink(root_key, self.auth_keys_dir + '/root')
        except OSError:
            pass

        # Hackish hook in rc.local to fix auth_keys_dir permission messed up by
        # cloud-init --> should be no longer needed

        try:
            f = open(self.sshd_conf, 'r')
            lines = f.readlines()
            f.close()
            reauth = r'^[ \t]*AuthorizedKeysFile'
            f = open(self.sshd_conf, 'w')
            for l in lines:
                if not re.match(reauth, l):
                    f.write(l)
            f.write( 'AuthorizedKeysFile %s/%%u\n' % self.auth_keys_dir )
            f.close()
        except IOError as e:
            print 'Problem configuring %s: %s' % (self.sshd_conf, e)

        # sudoers
        try:
            f = open(self.sudoers, 'r')
            lines = f.readlines()
            f.close()
            rek = r'.*keys_keeper\.sh'
            f = open(self.sudoers, 'w')
            for l in lines:
                if not re.match(rek, l):
                    f.write(l)
            f.write('Defaults!%s/keys_keeper.sh !requiretty\n' % self.sshcertauth_dst)
            f.write('apache ALL=(ALL) NOPASSWD: %s/keys_keeper.sh\n' % self.sshcertauth_dst)
            f.close()
        except IOError as e:
            print 'Problem configuring %s: %s' % (self.sshd_conf, e)

        # Restart affected services
        with open(os.devnull, 'w') as devnull:
            try:
                rs = subprocess.call('/sbin/service sshd restart'.split(' '), stdout=devnull)
                if rs != 0:
                    print "Error while restarting sshd: %d" % rs
                    return False
                rh = subprocess.call('/sbin/service httpd restart'.split(' '), stdout=devnull)
                if rh != 0:
                    print "Error while restarting httpd: %d" % rh
                    return False
            except OSError as e:
                print "Error restarting services: %s" % e
                return False

        return True


    def config_pool_users(self, num_pool_accounts):
        """Create pool group and accounts.
        """

        # Mapfile with appropriate permissions (rw for httpd user)
        try:
            if not os.path.isfile(self.auth_mapfile):
                f = open(self.auth_mapfile, 'w')
                f.close()

            httpd_uid = pwd.getpwnam(self.httpd_user).pw_uid
            os.chown(self.auth_mapfile, httpd_uid, 0)
            os.chmod(self.auth_mapfile, 0600)

        except (IOError, OSError, KeyError) as e:
            print "Cannot create mapfile %s with proper permissions: %s" % (self.auth_mapfile, e)
            return False

        # Create pool group and accounts
        with open(os.devnull, 'w') as devnull:
            try:

                r = subprocess.call(('groupadd -g %d %s' % (self.pool_gid, self.pool_group)).split(' '), stdout=devnull, stderr=devnull)
                if r != 0 and r != 9:
                    print "Error creating group %s: %d" % (self.pool_group, r)
                    return False

                for i in range(1, num_pool_accounts+1):

                    r = subprocess.call(
                        ('adduser pool%03u -s /bin/bash -u %u -g %d' % (i, self.pool_base_uid+i, self.pool_gid)).split(' '),
                        stdout=devnull,
                        stderr=devnull
                    )
                    # r == 9 means that the user already exists: this is OK
                    if r != 0 and r != 9:
                        print "Error creating user pool%03u: %d" % (i, r)
                        return False

            except OSError as e:
                print "Cannot create users and group: %s" % e
                return False

        return True


    def config_alice_ldap(self):
        """Configures LDAP authentication for ALICE users: also creates
        appropriate group.
        """

        # Create special ALICE group
        with open(os.devnull, 'w') as devnull:
            try:
                r = subprocess.call( ('groupadd -g %d %s' % (self.alice_gid, self.alice_group)).split(' '), stdout=devnull, stderr=devnull )
                if r != 0 and r != 9:
                    print "Error creating ALICE group %s: %d" % (self.alice_group, r)
            except OSError as e:
                print "Cannot create ALICE group: %s" % e
                return False

        # Configuring SSSD
        try:
            f = open(self.sssd_conf, 'w')
            f.write("""
[sssd]
config_file_version = 2
services = nss, pam
domains = default

[nss]
filter_users = root,ldap,named,avahi,haldaemon,dbus,radiusd,news,nscd
override_shell = /bin/bash
override_homedir = /home/%u
#override_gid = 99

[pam]

[domain/default]
ldap_tls_reqcert = never
auth_provider = ldap
ldap_schema = rfc2307bis
ldap_search_base = ou=People,o=alice,dc=cern,dc=ch
ldap_group_member = uniquemember
id_provider = ldap
ldap_id_use_start_tls = False
ldap_uri = ldap://aliendb06a.cern.ch:8389/
cache_credentials = True
ldap_tls_cacertdir = /etc/openldap/cacerts
entry_cache_timeout = 600
ldap_network_timeout = 3
ldap_access_filter = (objectclass=posixaccount)
ldap_user_uid_number = CCID
""")
            f.close()
        except IOError as e:
            print 'Cannot write SSSD configuration %s: %s' % (self.sssd_conf, e)
            return False

        # Mode
        try:
            os.chmod(self.sssd_conf, 0600)
        except OSError:
            print 'Cannot change permissions of %s' % self.sssd_conf
            return False

        # Enable auth options: notably, sssd (for LDAP) and mkhomedir
        with open(os.devnull, 'w') as devnull:

            try:
                r = subprocess.call( ('authconfig --enablesssd --enablesssdauth ' +
                    '--enablelocauthorize --enablemkhomedir --update').split(' '), stdout=devnull )
                if r != 0:
                    print "Error configuring the authentication mechanism: %d" % r
                    return False
            except OSError as e:
                print "Cannot call authconfig: %s" % e
                return False

            try:
                rc = subprocess.call('/sbin/chkconfig sssd on'.split(' '))
                if rc != 0:
                    print "Error while enabling sssd: %d" % rc
                    return False
                rs = subprocess.call('/sbin/service sssd restart'.split(' '), stdout=devnull)
                if rs != 0:
                    print "Error while restarting sssd: %d" % rs
                    return False
            except OSError as e:
                print "Error restarting services: %s" % e
                return False

        # Disable nscd cache on users and groups: sssd has its own
        try:
            f = open(self.nscd_conf, 'r')
            lines = f.readlines()
            f.close()
            recache = r'^[ \t]*enable-cache[ \t]+(group|passwd)[ \t]+.*$'
            f = open(self.nscd_conf, 'w')
            for l in lines:
                if not re.match(recache, l):
                    f.write(l)
            f.write('enable-cache passwd no\n')
            f.write('enable-cache group no\n')
            f.close()
        except IOError as e:
            print 'Problem configuring %s: %s' % (self.sshd_conf, e)

        # Flush nscd cache and restart service
        with open(os.devnull, 'w') as devnull:

            try:
                rs = subprocess.call('/sbin/service nscd restart'.split(' '), stdout=devnull)
                if rs != 0:
                    print "Error while restarting nscd: %d" % rs
                    return False
                rl = subprocess.call('/sbin/service nscd reload'.split(' '), stdout=devnull)
                if rl != 0:
                    print "Error while reloading nscd: %d" % rl
                    return False
            except OSError as e:
                print "Error with the nscd service: %s" % e
                return False

        return True


    def get_ipv4(self):
        """Guesses the IP(v4) of current host used for opening "outbound"
        connections.
        """
        try:
            # No data is actually transmitted (UDP)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect( ('8.8.8.8', 53) )
            real_ip = s.getsockname()[0]
            s.close()
            return real_ip
        except socket.error as e:
            print "Cannot retrieve current IPv4 address: %s" % e
            return
