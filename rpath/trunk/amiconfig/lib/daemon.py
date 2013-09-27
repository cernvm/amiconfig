#
# Copyright (c) 2008 rPath, Inc.
#

import os
import sys
import time

class Daemon(object):
    def start(self):
        """ Stub for subclasses to implement. """
        pass

    def daemonize(self):
        pid = os.fork()
        if pid == 0:
            null = os.open(os.devnull, os.O_RDONLY)
            os.dup2(null, sys.stdin.fileno())
            os.close(null)

            pid = os.fork()
            if pid == 0:
                os.setsid()
                sys.stdout.flush()
                sys.stderr.flush()

                self.start()
            else:
                time.sleep(1)
                timeSlept = 1
                while timeSlept < 60:
                    foundPid, status = os.waitpid(pid, os.WNOHANG)
                    if foundPid:
                        os._exit(0)
                    else:
                        time.sleep(.5)
                        timeSlept += .5
                os._exit(1)
        else:
            time.sleep(2)
            pid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status):
                rc = os.WEXITSTATUS(status)
                return rc
            else:
                print 'process killed with signal %s' % os.WTERMSIG(status)
                return 1
