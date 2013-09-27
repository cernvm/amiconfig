#!/bin/sh

AMICONFIG="/usr/sbin/amiconfig"
AMILOCK="/var/lock/subsys/amiconfig"
AMISETUP="/etc/sysconfig/amiconfig"

[ -f $AMICONFIG ] && [ -x $AMICONFIG ] || exit 1

###################################################################################################
runUserDataScript () {
###################################################################################################
  prog=$(basename $0)
  logger="logger -t $prog" 
  curl="curl --retry 3 --silent --show-error --fail --connect-timeout 60"
  ## 
  # Retrieve the instance user-data and run it if it looks like a script
  user_data_file=$(mktemp)
  $logger "Retrieving user-data"
  $curl -s $AMICONFIG_CONTEXT_URL/user-data | grep -v -e "^ *\$" > $user_data_file.tmp 2>&1 | $logger
  if [ "$(file -bi $user_data_file.tmp)" = "application/x-gzip" ]; then
    $logger "Uncompressing gziped user-data"
    mv $user_data_file.tmp $user_data_file.tmp.gz
    gunzip $user_data_file.tmp.gz
  fi
  if [ ! -s $user_data_file.tmp ]
  then
    $logger "No user-data available"
    rm -f $user_data_file.tmp
    return 1
  fi

  if [ `head -1 $user_data_file.tmp | grep -c -e '^#!'` -eq 0 ]
  then
    $logger 'Skipping user-data as it does not look like a script'
    rm -f $user_data_file.tmp
    return 1
  fi

  case $1 in
     before)
        awk '/#!.*sh.*before/,/^$/ {print}' $user_data_file.tmp >  $user_data_file  
        if [ ! -s $user_data_file ]
        then
          awk '/#!.*sh/,/^$/ {print}' $user_data_file.tmp >  $user_data_file  
          rm -f $user_data_file.tmp
        fi
        ;;
     after)
        awk '/#!.*sh.*after/,/^$/ {print}' $user_data_file.tmp >  $user_data_file  
        rm -f $user_data_file.tmp
        ;;
     *)
        return 1
        ;;
  esac

  $logger "Running user-data"
  chmod +x $user_data_file
  $user_data_file 2>&1 | logger -t "user-data"
  $logger "user-data exit code: $?"
  rm -f $user_data_file
  return 0 
}

###################################################################################################
###################################################################################################

if [ "x$AMICONFIG_CONTEXT_URL" = x ]
then
  ####
  # Test for EC2
  ####
  EC2_API_VERSIONS="2007-12-15"
  SERVER="169.254.169.254"
  for VERSION in $EC2_API_VERSIONS; do
      if [ -f /var/lib/amiconfig/$VERSION/user-data ]; then
         # Successful, update amiconfig
           echo "AMICONFIG_CONTEXT_URL=file:/var/lib/amiconfig/$VERSION/" > $AMISETUP
           break
      fi
      DATA=$(wget -t1 -T1 -q -O - http://169.254.169.254/$VERSION/user-data)
      if [ $? -eq 0 ]; then
         # Successful, update amiconfig
           echo "AMICONFIG_CONTEXT_URL=http://$SERVER/$VERSION/" >  $AMISETUP
           mkdir -p  /var/lib/amiconfig/$VERSION
           echo "$DATA" > /var/lib/amiconfig/$VERSION/user-data 
           break
      fi
  done 
  ####
  # Test for CloudStack
  # Find the leases in every interface
  if [ -d  /var/lib/dhclient ]
  then
    LEASES=$(ls /var/lib/dhclient/*.leases)
    # Check if we are running a metadata server on the dhcp-identifier
    # specified on every interface
    for LEASE in $LEASES; do
      SERVER=$(cat $LEASE | grep dhcp-server-identifier)
      if [ ! -z "$SERVER" ]; then
         SERVER=$(echo "$SERVER" | awk '{print $3}' | tr -d ';' | tr -d '\n' | tail -n1 )
         if [ ! -z "$SERVER" ]; then
             # Try to perform an HTTP get request
             DATA=$(wget -t1 -T1 -q -O - http://$SERVER/latest/user-data)
             if [ $? -eq 0 -a ! -z "$DATA" ]; then
                 # Successful, update amiconfig
                 echo "AMICONFIG_CONTEXT_URL=http://$SERVER/latest/" >  $AMISETUP
                 mkdir -p  /var/lib/amiconfig/latest
                 echo "$DATA" > /var/lib/amiconfig/latest/user-data 
                 break
             fi
          fi
       fi
    done
  fi
fi

if [ -z "$AMICONFIG_CONTEXT_URL" ]; then
     [ -f $AMISETUP ] && . $AMISETUP
     export AMICONFIG_CONTEXT_URL
fi

#$AMICONFIG --probe 2>/dev/null || exit $?

case $1 in
   user)
     runUserDataScript before
     $AMICONFIG
     runUserDataScript after
     ;;
   hepix)
     $AMICONFIG -f hepix
     ;;
esac
   

