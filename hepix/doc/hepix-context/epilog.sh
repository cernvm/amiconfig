#!/bin/bash
#
# epilog.sh: site contextualization script - template
#
# Source function library
. /etc/init.d/functions

start() {    
    #
    # source environment for contextualization
    #
    echo "Epilog::start()"
    #
    # put your code to be run at boot time here
    #

    RETVAL=$?
    return $RETVAL
}

stop() {
    #
    # source environment for contextualization
    #
    echo "Epilog::stop()"
    #
    # put your code to be run at shutdown time here
    #

    RETVAL=$?
    return $RETVAL
}

case "$1" in
    start)
#               [ $running -eq 0 ] && exit 0
                start
                RETVAL=$?
                ;;
    stop)
#               [ $running -eq 0 ] || exit 0
                stop
                RETVAL=$?
                ;;
        *)
        echo $"Usage: $0 {start|stop}"
        RETVAL=2
esac

exit $RETVAL
