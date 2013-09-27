#
# Copyright (c) 2004-2009 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/cpl.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

all: subdirs

SUBDIRS=

python_files = \
	conaryproxy.py \
	dnsupdate.py \
	hostname.py \
	kernelmodules.py \
	noip.py \
	openvpn.py \
	rapadminpassword.py \
	rapcert.py \
	raprsakey.py \
	rmakenode.py \
	rmakeplugin.py \
	rmakeserver.py \
	rootsshkeys.py \
	rpathplugin.py \
	sfcbclient.py \
	storage.py \
	disablesshpasswdauth.py

extra_files = \
	Makefile

dist_files = $(python_files) $(extra_files)

generated_files = *.pyo *.pyc 

.PHONY: clean dist install subdirs

subdirs: default-subdirs

constants.py: constants.py.in ../Makefile
	sed s,@version@,$(VERSION),g $< > $@

install: all install-subdirs pyfiles-install
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"
	$(PYTHON) -OO -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"

dist: default-dist

clean: clean-subdirs default-clean

include ../../Make.rules
