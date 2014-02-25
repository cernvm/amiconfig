#
# Copyright (c) 2008 rPath Inc.
#

import os
import string
import fileinput
from random import choice

from subprocess import call

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'squid'

    def configure(self):
        """
        [squid]
        backends = server1.cern.ch,server2.fnal.gov,...
        cache_dir = /var/spool/squid
        cache_dir_size = 50000
        """

        cfg = self.ud.getSection('squid')
	output = []
	guard_comment = '# added by CernVM contextualization'

	output.append("max_filedesc 8192")
	output.append("maximum_object_size 1024 MB")
	output.append("cache_mem 128 MB")
	output.append("maximum_object_size_in_memory 128 KB")

	cache_dir = '/var/spool/squid'
        if 'cache_dir' in cfg:
            cache_dir = cfg['cache_dir']
	cache_dir_size = '50000'
        if 'cache_dir_size' in cfg:
            cache_dir_size = cfg['cache_dir_size']
	output.append("cache_dir ufs %s %s 16 256" % (cache_dir, cache_dir_size))
		

	if 'backends' in cfg:
		backends = cfg['backends']
		servers = backends.split(',')
		for server in servers:
			output.append("acl backend dst %s" % server)
		output.append("http_access allow backend")

	if len(output):
		os.system("sed -i -e '/include \/etc\/squid\/cernvm.conf/d' /etc/squid/squid.conf");
		for linenum,line in enumerate(fileinput.FileInput("/etc/squid/squid.conf", inplace=1)):
			if linenum==0:
				print "include /etc/squid/cernvm.conf"
			print line.rstrip() 
		output.append('')
 		f = open('/etc/squid/cernvm.conf', 'w')
		f.write('\n'.join(output))
		f.close()
		os.system("sed -i -e '/ulimit -n/d' /etc/sysconfig/squid");
		f = open('/etc/sysconfig/squid', 'a')
                f.write('ulimit -n 10000\n')
                f.close()
	
	os.system("/sbin/chkconfig squid on")
	os.system("squid -z")
	os.system("/sbin/service squid start")
