#
# Copyright (c) 2009 rPath, Inc.
#

import base64
import os
import sys

from conary.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'sfcb-client-setup'
    _sectionName = 'sfcb-client-setup'

    def configure(self):
        cfg = self.ud.getSection(self._sectionName)
        if not cfg:
            return

        # Get boot uuid
        bootUuidField = 'boot-uuid'
        if bootUuidField in cfg:
            bootUuid = cfg[bootUuidField]
            bootUuidFile = "/etc/conary/rpath-tools/boot-uuid"
            util.mkdirChain(os.path.dirname(bootUuidFile))
            file(bootUuidFile, "w").write(bootUuid.strip())

        # Get the cert name
        certHashField = 'x509-cert-hash'
        certField = 'x509-cert(base64)'
        if certHashField not in cfg or certField not in cfg:
            return

        x509CertHash = cfg[certHashField]
        if not x509CertHash.endswith('.0'):
            x509CertHash += '.0'
        x509Cert = cfg[certField]
        try:
            x509Cert = base64.decodestring(x509Cert)
        except:
            # Malformed base64 data. We ignore it.
            return
        sfcbConfigDir = self.getSfcbConfigDir()
        if sfcbConfigDir is None:
            return
        certsDir = os.path.join(sfcbConfigDir, "clients")
        certsFileName = os.path.join(certsDir, os.path.basename(x509CertHash))
        # Exceptions are properly displayed by ami.py
        util.mkdirChain(certsDir)
        file(certsFileName, "w").write(x509Cert)

    def getSfcbConfigDir(self):
        configDirs = [
            os.path.join(os.sep, "etc", "conary", "sfcb"),
            os.path.join(os.sep, "etc", "sfcb"),
        ]
        for configDir in configDirs:
            if not os.path.isdir(configDir):
                continue
            cfgFilePath = os.path.join(configDir, "sfcb.cfg")
            if os.path.isfile(cfgFilePath):
                return configDir
        return None
