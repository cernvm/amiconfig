# Copyright (c) 2006-2008 rPath, Inc.
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

TOPDIR = ..

extra_files = Makefile

dist_files = ami.init $(extra_files)

all:

install:
	mkdir -p $(DESTDIR)$(initdir)
	install -m 755 ami.init $(DESTDIR)$(initdir)/amiconfig

dist : $(dist_files) default-dist

clean : default-clean

include $(TOPDIR)/Make.rules

.PHONY: clean dist install
