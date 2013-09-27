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

export VERSION = 0.5.0
export TOPDIR = $(shell pwd)
export DISTDIR = $(TOPDIR)/amiconfig-$(VERSION)
export sysconfdir = /etc
export initdir = $(sysconfdir)/init.d
export prefix = /usr
export bindir = $(prefix)/bin
export sbindir = $(prefix)/sbin
export libdir = $(prefix)/lib
export libexecdir = $(prefix)/libexec
export datadir = $(prefix)/share
export mandir = $(datadir)/man
export sitedir = $(libdir)/python$(PYVERSION)/site-packages/
export amiconfigdir = $(sitedir)/amiconfig
export amiconfiglibdir = $(libdir)/amiconfig
export amiconfiglibexecdir = $(libexecdir)/amiconfig

SUBDIRS = commands amiconfig extra

extra_files = \
	LICENSE			\
	Make.rules 		\
	Makefile		\
	NEWS			\

dist_files = $(extra_files)

.PHONY: clean dist install subdirs

subdirs: default-subdirs

install: install-subdirs

dist:
	if ! grep "^Changes in $(VERSION)" NEWS > /dev/null 2>&1; then \
		echo "no NEWS entry"; \
		exit 1; \
	fi
	$(MAKE) forcedist

archive:
	rm -rf $(DISTDIR)
	mkdir $(DISTDIR)
	for d in $(SUBDIRS); do make -C $$d DIR=$$d dist || exit 1; done
	for f in $(dist_files); do \
		mkdir -p $(DISTDIR)/`dirname $$f`; \
		cp -a $$f $(DISTDIR)/$$f; \
	done; \
	tar cjf $(DISTDIR).tar.bz2 `basename $(DISTDIR)` ; \
	rm -rf $(DISTDIR)

forcedist: $(dist_files) archive

tag:
	hg tag amiconfig-$(VERSION)

clean: clean-subdirs default-clean

ccs: dist
	cvc co --dir amiconfig-$(VERSION) amiconfig=conary.rpath.com@rpl:devel
	sed -i 's,version = ".*",version = "$(VERSION)",' \
                                        amiconfig-$(VERSION)/amiconfig.recipe;
	sed -i 's,r.addArchive.*,r.addArchive("amiconfig-$(VERSION).tar.bz2"),' \
                                        amiconfig-$(VERSION)/amiconfig.recipe;
	cp amiconfig-$(VERSION).tar.bz2 amiconfig-$(VERSION)
	bin/cvc cook amiconfig-$(VERSION)/amiconfig.recipe
	rm -rf amiconfig-$(VERSION)

include Make.rules
