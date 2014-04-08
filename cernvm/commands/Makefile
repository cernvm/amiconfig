#
# Copyright (c) 2005 rPath, Inc.
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

TOPDIR=..

bin_files = \
	amiconfig-mime

sbin_files = \
	amiconfig-helper

extra_dist = \
	Makefile \

dist_files = $(bin_files) $(sbin_files) $(extra_dist)

all: default-all

install-mkdirs:
	mkdir -p $(DESTDIR)$(sbindir)
	mkdir -p $(DESTDIR)$(bindir)

install: install-mkdirs
	for f in $(sbin_files); do \
		install -m755 $$f $(DESTDIR)$(sbindir)/$$f; \
	done
	for f in $(bin_files); do \
                install -m755 $$f $(DESTDIR)$(bindir)/$$f; \
        done

dist: default-dist

clean: default-clean

include $(TOPDIR)/Make.rules
