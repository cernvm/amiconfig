#!/bin/bash
#
# prolog.sh: site contextualization script - template
#
# Source function library
. /etc/init.d/functions

start() {    
    #
    # source environment for contextualization
    #
    if [ -f ./context.sh ]; then
        . ./context.sh
    elif [ -f $CONTEXT_DIR/context.sh ]; then
        . $CONTEXT_DIR/context.sh
    fi
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
    if [ -f ./context.sh ]; then
        . ./context.sh
    elif [ -f $CONTEXT_DIR/context.sh ]; then
        . $CONTEXT_DIR/context.sh
    fi
    /bin/true
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
