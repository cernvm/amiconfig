#
# Copyright (c) 2011 CERN
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

from optparse import OptionParser, Option

CONFIGFILE = '/etc/amiconfig/default.cfg'

optionsTable = [
    Option('-d', '--debug', action="store_true",
        help="Run in debugging mode"),
    Option('-p', '--probe', action="store_true",
        help="Probe if the metadata service is available"),
    Option('-c', '--config', dest="configfile", default=CONFIGFILE,
        help="Alternative configuration file (default is /etc/amiconfig/default.cfg)"),
    Option('-f', '--force', dest="forced_plugins", 
        help=("Comma-separated list of enforced plugins. "
              "Only listed plugins will be run.")),
]
optparser = OptionParser(option_list=optionsTable)
options, args = optparser.parse_args()
