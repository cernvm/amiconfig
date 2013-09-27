#
# Copyright (c) 2004-2008 rPath, Inc.
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

all: subdirs constants.py

SUBDIRS=plugins lib

python_files = \
	__init__.py \
	ami.py \
	constants.py \
	errors.py \
	instancedata.py \
	metadataservice.py \
	plugin.py \
	userdata.py

extra_files = \
	Makefile \
	constants.py.in

dist_files = $(python_files) $(extra_files)

generated_files = *.pyo *.pyc 

.PHONY: clean dist install subdirs

subdirs: default-subdirs

constants.py: constants.py.in ../Makefile
	sed -e s,@version@,$(VERSION),g $< > $@
	sed -i s,@amiconfigdir@,$(amiconfigdir),g $@
	sed -i s,@libdir@,$(libdir),g $@

install: all install-subdirs pyfiles-install
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"
	$(PYTHON) -OO -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"

dist: default-dist

clean: clean-subdirs default-clean
	rm -f constants.py

include ../Make.rules
