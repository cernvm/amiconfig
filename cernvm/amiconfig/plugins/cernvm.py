#
# Copyright (c) 2008 rPath Inc.
#

import os
import sys
import stat
import string
import base64
import pwd
import random
import re
import shutil

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'cernvm'

    def read(self, filename):
        f = open(filename)
        content = f.read()
        f.close()
        return content

    def write(self, filename, content):
        f = open(filename, "w")
        f.write(content)
        f.close()

    def writeConfigToFile(self, filename, key, val, delimiter):
        content = ""
        try:
            content = self.read(filename)
        except IOError, e:
            # Maybe the file doesn't exist, so ignore.
            pass

        content = "\n" + content.strip() + "\n"
        if val:
            val = "%s%s%s" % (key, delimiter, val)
        start = 0
        indexKey = content.find("\n" + key, start)
        if -1 == indexKey and val:
            content += "%s\n" % (val)
        while -1 != indexKey:
            indexEnd = content.find("\n", indexKey+1)
            assert indexEnd > indexKey
            if not val or 0 != start:
                content = "%s%s" % (content[:indexKey], content[indexEnd:])
                start = indexKey
            else:
                content = "%s\n%s%s" % (content[:indexKey], val,
                         content[indexEnd:])
                start = indexKey + 1 + len(val)

            indexKey = content.find("\n" + key, start)

        self.write(filename, content.lstrip())


    def configure(self):
        """
        [cernvm]
        # entitlement key
        entitlement_key = 289a919c-9a97-44a9-a07d-473850bd5730 
        # contextualization key
        contextualization_key = de4248a0-3fc9-463b-a66f-88f7bc935b11
        # path to contextualization command
        contextualization_command = /path/to/script.sh
        # url to retrieve initial CernVM configuration
        # config_url = <url>
        # list of ',' seperated organisations/experiments
        organisations = alice,atlas
        # install group profile
        group_profile = group-<org>[-desktop]
        # list of ',' seperated repositories
        repositories = alice,atlas,grid
        # CernVM user name:group:password
        users = testalice:alice:12345test,testatlas:atlas:12345atlas
        # CernVM user shell </bin/bash|/bin/tcsh>
        shell = /bin/bash
        # Automatically login CernVM user to GUI
        auto_login = on
        # CVMFS HTTP proxy http://<host>:<port>;DIRECT
        proxy = DIRECT
        # list of ',' seperated services to start
        services = <list>
        # extra environment variables to define
        environment = CMS_SITECONFIG=CERN,CMS_ROOT=/opt/cms
        # CernVM edition Basic|Desktop
        edition = Basic
        # CernVM screen Resolution
        screenRes = 1024x768
        # Start XDM on boot  on|off
        startXDM = off
        # Keyboard
        keyboard = us
        # GRID UI version
        gridUiVersion = default
        """

        cfg = self.ud.getSection('cernvm')
        
        group_profile = ''
        if 'group_profile' in cfg:
            group_profile = cfg['group_profile']
            call(['/etc/cernvm/config',
                             '-g',
                             '%s' % (group_profile)])
            
        entitlement_key = ''
        if 'entitlement_key' in cfg:
            entitlement_key = cfg['entitlement_key']
            self.writeConfigToFile(
                "/etc/cvmfs/site.conf",
                'CVMFS_ENTITLEMENT_KEY',entitlement_key,"=")

        contextualization_key = ''
        if 'contextualization_key' in cfg:
            contextualization_key = cfg['contextualization_key']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_CONTEXTUALIZATION_KEY',contextualization_key,"=")

        contextualization_cmd = ''
        if 'contextualization_command' in cfg:
            contextualization_cmd = cfg['contextualization_command']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_CONTEXTUALIZATION_COMMAND',
                contextualization_cmd,"=")
    
        organisations = ''
        if 'organisations' in cfg:
            organisations = cfg['organisations']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_ORGANISATION',organisations,"=")

        repositories = ''
        if 'repositories' in cfg:
            repositories = cfg['repositories']
            self.writeConfigToFile(
                "/etc/cvmfs/site.conf",
                'CVMFS_REPOSITORIES',repositories,"=")

        screenRes = ''
        if 'screenres' in cfg:
            screenRes = cfg['screenres']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_SCREEN_RES',screenRes,"=")

        startXDM = ''
        if 'startxdm' in cfg:
            startXDM = cfg['startxdm']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_START_XDM',startXDM,"=")

        edition = ''
        if 'edition' in cfg:
            edition = cfg['edition']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_EDITION',edition,"=")

        keyboard = ''
        if 'keyboard' in cfg:
            keyboard = cfg['keyboard']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_KEYBOARD',keyboard,"=")

        gridUiVersion = ''
        if 'griduiversion' in cfg:
            gridUiVersion = cfg['griduiversion']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_GRID_UI_VERSION',gridUiVersion,"=")


        #config_url = ''
        #if 'config_url' in cfg:
        #    config_url = cfg['config_url']
        #    self.writeConfigToFile(
        #        "/etc/cernvm/site.conf",
        #        'CERNVM_CONFIG_URL',config_url,"=")

        proxy = ''
        if 'proxy' in cfg:
            proxy = cfg['proxy']
            self.writeConfigToFile(
                "/etc/cvmfs/site.conf",
                'CVMFS_HTTP_PROXY',proxy,"=")

        services = ''
        if 'services' in cfg:
            services = cfg['services']
            self.writeConfigToFile(
                "/etc/cernvm/site.conf",
                'CERNVM_SERVICES',services,"=")

        shell = '/bin/bash'
        if 'shell' in cfg:
            shell = cfg['shell']
        self.writeConfigToFile(
            "/etc/cernvm/site.conf",
            'CERNVM_USER_SHELL',shell,"=")

        autoLogin = 'off'
        if 'auto_login' in cfg:
            autoLogin = cfg['auto_login']
        self.writeConfigToFile(
            "/etc/cernvm/site.conf",
            'CERNVM_AUTOLOGIN',autoLogin,"=")

        if 'desktop_icons' in cfg:
            desktopIcons = cfg['desktop_icons']
            self.writeConfigToFile(
              "/etc/cernvm/site.conf",
              'CERNVM_DESKTOP_ICONS', desktopIcons, "=")
            util.call(['/etc/cernvm/config','-y'])

        environment = ''
        vars = ''
        if 'environment' in cfg:
            environment = cfg['environment']
            for entry in environment.split(','):
                (var,val) = entry.split('=')
                self.writeConfigToFile(
                    "/etc/cernvm/environment.conf",var,val,"=")
                vars += '+' + var
                   
            self.writeConfigToFile(
                    "/etc/cernvm/site.conf",'CERNVM_ENVIRONMENT_VARS',vars,'=')

        users = ''
        first = 1
        eosUser = None
        x509User = None
        if 'users' in cfg:
            users = cfg['users']
            for entry in users.split(','):
                 (username,group,password) = entry.split(':')
                 if not len(password):
                     password = ''.join(random.choice(string.ascii_uppercase +
                                                      string.digits +
                                                      string.ascii_lowercase)
                                        for x in range(8))
                 if first:
                     self.writeConfigToFile(
                          "/etc/cernvm/site.conf",
                          'CERNVM_USER',username,"=")
                     self.writeConfigToFile(
                         "/etc/cernvm/site.conf",
                         'CERNVM_USER_GROUP',group,"=")
                     first = 0 
                     x509User = username
                     eosUser  = username
                 call(['/etc/cernvm/config',
                             '-u',
                             '%s' % (username),
                             '%s' % (shell),
                             '%s' % (password),
                             '%s' % (group)]) 

        certUserField = 'x509-user'
        if certUserField in cfg:
            x509User = cfg[certUserField]

        if x509User is None:
            # Fallback to root
            x509User = 'root'

        certFileField = 'x509-cert-file'
        if certFileField in cfg and x509User is not None:
            pw = pwd.getpwnam(x509User)
            x509CertFile = '/tmp/x509up_u' + str(pw.pw_uid)
            eosx509CertFile = x509CertFile
            shutil.copy2(cfg[certFileField], x509CertFile)
            os.chmod(x509CertFile,stat.S_IREAD|stat.S_IWRITE)
            os.chown(x509CertFile,pw.pw_uid,pw.pw_gid)

        certField = 'x509-cert'
        if  certField in cfg and x509User is not None:
            x509Cert = cfg[certField]
            try:
                x509Cert = base64.decodestring(x509Cert)
            except:
                # Malformed base64 data. We ignore it.
                return
            pw = pwd.getpwnam(x509User)
            x509CertFile = '/tmp/x509up_u' + str(pw.pw_uid)
            eosx509CertFile = x509CertFile
            file(x509CertFile, "w").write(x509Cert)
            os.chmod(x509CertFile,stat.S_IREAD|stat.S_IWRITE)
            os.chown(x509CertFile,pw.pw_uid,pw.pw_gid)

        eosUserField = 'eos-user'
        if  eosUserField in cfg:
            eosUser = cfg[eosUserField]

        eosCertField = 'eos-x509-cert'
        if  eosCertField in cfg:
            eosx509Cert = cfg[eosCertField]
            try:
                eosx509Cert = base64.decodestring(eosx509Cert)
            except:
                # Malformed base64 data. We ignore it.
                return
            pw = pwd.getpwnam(eosUser)
            eosx509CertFile = '/tmp/x509up_u' + str(pw.pw_uid) + '.eos' 
            file(eosx509CertFile, "w").write(eosx509Cert)
            os.chmod(eosx509CertFile,stat.S_IREAD|stat.S_IWRITE)
            os.chown(x509CertFile,pw.pw_uid,pw.pw_gid)

        field  = 'eos-readaheadsize'
        eosReadAheadSize = 4000000 
        if  field in cfg:
            eosReadAheadSize = cfg[field]
            
        field  = 'eos-readcachesize'
        eosReadCacheSize = 16000000 
        if  field in cfg:
            eosReadCacheSize = cfg[field]
            
        srvField  = 'eos-server'
        if  srvField in cfg and eosUser is not None:
            server   = cfg[srvField]
            util.mkdirChain('/eos')
            util.call(['/bin/chown',eosUser,'/eos']) 
            util.call(['/sbin/modprobe','fuse']) 
            cmd='/usr/bin/env X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates X509_USER_PROXY=%s EOS_READAHEADSIZE=%s EOS_READCACHESIZE=%s /usr/bin/eosfsd /eos -oallow_other,kernel_cache,attr_timeout=30,entry_timeout=30,max_readahead=131072,max_write=4194304,fsname=eos root://%s//eos/'  % (eosx509CertFile,eosReadAheadSize,eosReadCacheSize,server)
            util.call(cmd.split())

        if  edition == 'Desktop':
            util.call(['/etc/cernvm/config','-x']) 
            util.call(['/sbin/telinit','5']) 
