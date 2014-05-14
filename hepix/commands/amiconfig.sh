#!/bin/bash

AMICONFIG="/usr/sbin/amiconfig"
AMILOCK="/var/lock/subsys/amiconfig"
AMISETUP="/etc/sysconfig/amiconfig"

# Where to look for injected extra user-data
AMI_EXTRA_USER_DATA="/cernvm/extra-user-data"

# A lock file to signal appended user-data
AMI_DONE_EXTRA_APPENDED='/var/lib/amiconfig/extra-appended.done'

# Maximum number of retries when attempting to retrieve user-data
AMI_DOWNLOAD_RETRIES=2

# Timeout, in seconds, to retrieve user-data
AMI_DOWNLOAD_TIMEOUT_S=20

# Lock files: to prevent recontextualization at reboot
AMI_DONE_USER='/var/lib/amiconfig/user.done'
AMI_DONE_HEPIX='/var/lib/amiconfig/hepix.done'

if [ "$AMILOGECHO" != '' ] && [ "$AMILOGECHO" != '0' ] ; then
  LOGGER="echo :: "
  PIPELOGGER="cat"
else
  LOGGER="logger -t amiconfig.sh"
  PIPELOGGER="logger -t amiconfig.sh"
fi

# Retrieves user-data and uncompresses it. Returns 0 on success (in such case,
# environment and files are in place), 1 on failure. If user-data is compressed,
# uncompresses it
RetrieveUserData() {

  if [ "$AMICONFIG_CONTEXT_URL" != '' ] ; then

    # If context URL is found, it's from the environment. We must fill manually
    # the "local copy", where applicable
    $LOGGER "Won't check for new URLs: found from environment: $AMICONFIG_CONTEXT_URL"

    if [ "$AMICONFIG_LOCAL_USER_DATA" == '' ] ; then
      if [ ${AMICONFIG_CONTEXT_URL:0:5} == 'file:' ] ; then

        # Set local user data by stripping file
        export AMICONFIG_LOCAL_USER_DATA="${AMICONFIG_CONTEXT_URL:5}/user-data"

      elif [ ${AMICONFIG_CONTEXT_URL:0:1} == '/' ] ; then

        # Just append user-data
        export AMICONFIG_LOCAL_USER_DATA="${AMICONFIG_CONTEXT_URL}/user-data"

      else

        # Attempt to retrieve from the given URL
        LOCAL_USER_DATA="/var/lib/amiconfig/custom/"
        mkdir -p "$LOCAL_USER_DATA"
        wget -t$AMI_DOWNLOAD_RETRIES -T$AMI_DOWNLOAD_TIMEOUT_S -q -O $LOCAL_USER_DATA/user-data $AMICONFIG_CONTEXT_URL/user-data 2> /dev/null
        if [ $? == 0 ] ; then
          $LOGGER "Data from environment URL $AMICONFIG_CONTEXT_URL saved to $LOCAL_USER_DATA"
          export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}/user-data"
        else
          $LOGGER "Can't retrieve data from environment URL $AMICONFIG_CONTEXT_URL: trying to proceed anyway"
        fi

      fi

      # Remove double slashes (except in front of protocol specification, e.g. http://)
      export AMICONFIG_CONTEXT_URL=$(echo "$AMICONFIG_CONTEXT_URL" | sed -e 's#\([^:]\)/\+#\1/#g')
      export AMICONFIG_LOCAL_USER_DATA=$(echo "$AMICONFIG_LOCAL_USER_DATA" | sed -e 's#/\+#/#g')

    fi

  else

    RetrieveUserDataCvmOnline || RetrieveUserDataEC2 || RetrieveUserDataCloudStack || RetrieveUserDataGCE
    if [ $? != 0 ] ; then
      $LOGGER "No standard user-data can be retrieved from any standard source: we are going to check for extra injected user data"
    fi

  fi

  # At this point, user-data is available locally. Let's uncompress it if needed
  if [ "$(file -bi $AMICONFIG_LOCAL_USER_DATA 2> /dev/null)" == "application/x-gzip" ] ; then
    $LOGGER "user-data is compressed: uncompressing it"
    cat "$AMICONFIG_LOCAL_USER_DATA" | gunzip > "$AMICONFIG_LOCAL_USER_DATA".0
    if [ -s "$AMICONFIG_LOCAL_USER_DATA".0 ] ; then
      $LOGGER "user-data uncompressed"
      mv "$AMICONFIG_LOCAL_USER_DATA".0 "$AMICONFIG_LOCAL_USER_DATA"
      chmod 0600 "$AMICONFIG_LOCAL_USER_DATA"
    else
      # Failure in uncompressing is non-fatal
      $LOGGER "Failure uncompressing user-data: leaving original user-data there"
    fi
  fi

  # Now we retrieve the extra user data (which is never compressed) and append it, if it exists
  if [ ! -e "$AMI_DONE_EXTRA_APPENDED" ] ; then
    RetrieveUserDataInjected && touch "$AMI_DONE_EXTRA_APPENDED"
  else
    $LOGGER "Extra injected user-data already appended, skipping"
  fi

  # Hard failure only if no user-data can be found either from standard location and extra injected path
  if [ ! -r "$AMICONFIG_LOCAL_USER_DATA" ] ; then
    return 1
  fi

  return 0

}

# Retrieve injected user data. Injected user-data does not exclude other
# user-data sources, but it is always appended to existing user-data. In some
# cases the injected extra user-data can be the only source: this case is
# appropriately dealt with. Returns 1 on failure, 0 if found
RetrieveUserDataInjected() {

  # Fall back to this path if no existing user-data is there already
  LOCAL_USER_DATA='/var/lib/amiconfig/2007-12-15'

  if [ -r "$AMI_EXTRA_USER_DATA" ] ; then

    $LOGGER "Extra injected configuration: additional user-data found at $AMI_EXTRA_USER_DATA"

    if [ "$AMICONFIG_CONTEXT_URL" == '' ] ; then

      $LOGGER "Extra injected configuration: this is the only user-data source available"

      # This is the only user-data! Set variables properly and save permanently
      mkdir -p "$LOCAL_USER_DATA"
      export AMICONFIG_CONTEXT_URL="file:$LOCAL_USER_DATA"
      export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}/user-data"
      echo "export AMICONFIG_CONTEXT_URL=$AMICONFIG_CONTEXT_URL" > $AMISETUP

      # Add a newline at the end (might be missing)
      echo '' > "$AMICONFIG_LOCAL_USER_DATA"

    else

      $LOGGER "Extra injected configuration: appending configuration to current user-data at $AMICONFIG_LOCAL_USER_DATA"

    fi

    # Append extra injected user-data
    cat "$AMI_EXTRA_USER_DATA" >> "$AMICONFIG_LOCAL_USER_DATA"
    chmod 0600 "$AMICONFIG_LOCAL_USER_DATA"

    return 0  # success (found)

  fi

  $LOGGER "Extra injected configuration: no injected user-data found at $AMI_EXTRA_USER_DATA"
  return 1  # failure (not found)

}

# Tries to check for the user-data file left there from CernVM Online.
# Returns 0 on success, 1 on failure
RetrieveUserDataCvmOnline() {

  LOCAL_USER_DATA='/var/lib/amiconfig-online/2007-12-15'
  CHECK_SILENT='--check-silent'

  if [ -e "$LOCAL_USER_DATA/user-data" ] ; then
    if [ "$1" != "$CHECK_SILENT" ] ; then
      $LOGGER "CernVM Online: local user data found at $LOCAL_USER_DATA"
      export AMICONFIG_CONTEXT_URL="file:$LOCAL_USER_DATA"
      export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}/user-data"
      echo "export AMICONFIG_CONTEXT_URL=$AMICONFIG_CONTEXT_URL" > $AMISETUP
    fi
    return 0
  fi

  if [ "$1" != "$CHECK_SILENT" ] ; then
    $LOGGER "CernVM Online: no user-data found at $LOCAL_USER_DATA"
  fi
  return 1

}

# Trying to contact the EC2 metadata server. Returns 0 on success, 1 on
# failure. The user-data is saved locally
RetrieveUserDataEC2() {

  # EC2 metadata server versions
  EC2_API_VERSIONS="2007-12-15"
  SERVER="169.254.169.254"
  DEFAULT_URL="http://$SERVER/$(echo $EC2_API_VERSIONS|awk '{ print $1 }')/"

  # Local checks
  for VERSION in $EC2_API_VERSIONS ; do

    LOCAL_USER_DATA="/var/lib/amiconfig/$VERSION/"

    if [ -f $LOCAL_USER_DATA/user-data ] ; then
      # Found user-data locally. Update configuration

      # We should just rely on the local user data without actually updating the configuration
      $LOGGER "EC2: user-data found locally, won't download again: $LOCAL_USER_DATA"
      export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}user-data"

      if [ -f "$LOCAL_USER_DATA"/meta-data ] ; then
        # It seems that metadata exists there. We should point amiconfig to the
        # local directory in such case
        $LOGGER "EC2: user-data found locally, updating configuration: $LOCAL_USER_DATA"
        echo "AMICONFIG_CONTEXT_URL=file:$LOCAL_USER_DATA" > $AMISETUP
        export AMICONFIG_CONTEXT_URL="file:$LOCAL_USER_DATA"
      else
        # Metadata not found locally. Set the URL currently in file. If not there, warn the user
        [ -e $AMISETUP ] && source $AMISETUP
        export AMICONFIG_CONTEXT_URL
        if [ "$AMICONFIG_CONTEXT_URL" == '' ] ; then
          $LOGGER "EC2: no metadata found locally and no context URL is set: will use the default: $DEFAULT_URL"
          echo "AMICONFIG_CONTEXT_URL=$DEFAULT_URL" > $AMISETUP
          export AMICONFIG_CONTEXT_URL="$DEFAULT_URL"
        fi
      fi

      # Proper permissions
      chmod 0600 "$AMICONFIG_LOCAL_USER_DATA"

      # If we exit here, everything is consistent
      return 0
    fi

  done

  # If we are here, no user-data has been found locally. Look for HTTP metadata
  $LOGGER "EC2: no local user-data found: trying metadata HTTP server $SERVER instead"

  # Remote check. Can we open a TCP connection to the server?
  nc -w 1 $SERVER 80 > /dev/null 2>&1
  if [ $? == 0 ] ; then

    $LOGGER "EC2: metadata server $SERVER seems to respond"

    # Check all possible remote versions
    for VERSION in $EC2_API_VERSIONS ; do

      LOCAL_USER_DATA="/var/lib/amiconfig/$VERSION/"
      REMOTE_USER_DATA="http://$SERVER/$VERSION/"
      DATA=$(wget -t$AMI_DOWNLOAD_RETRIES -T$AMI_DOWNLOAD_TIMEOUT_S -q -O - $REMOTE_USER_DATA/user-data 2> /dev/null)
      if [ $? == 0 ] ; then
        $LOGGER "EC2: user-data downloaded from $REMOTE_USER_DATA and written locally"

        # Write file there for script
        mkdir -p "$LOCAL_USER_DATA"
        echo "$DATA" > "$LOCAL_USER_DATA"/user-data
        chmod 0600 "$LOCAL_USER_DATA"/user-data

        # Export local location
        export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}user-data"

        # Pass remote URL there for metadata (used by amiconfig)
        echo "AMICONFIG_CONTEXT_URL=$REMOTE_USER_DATA" > $AMISETUP
        export AMICONFIG_CONTEXT_URL="$REMOTE_USER_DATA"

        # Exit consistently (user-data written, env exported, settings saved)
        return 0
      fi

    done

  fi

  # Error condition (no env exported, no file written)
  $LOGGER "EC2: can't find any user-data"
  return 1

}


# Trying to contact the GCE metadata server. Returns 0 on success, 1 on
# failure. The user-data is saved locally
RetrieveUserDataGCE() {
  # GCE metadata server versions
  GCE_API_VERSION="v1"
  SERVER="169.254.169.254"
  DEFAULT_URL="http://$SERVER/computeMetadata/${GCE_API_VERSION}/instance/attributes"

  # Local check
  LOCAL_USER_DATA="/var/lib/amiconfig/${GCE_API_VERSION}"
  if [ -f $LOCAL_USER_DATA/user-data ] ; then
    # Found user-data locally. Update configuration
    # We should just rely on the local user data without actually updating the configuration
    $LOGGER "GCE: user-data found locally, won't download again: $LOCAL_USER_DATA"
    export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}/user-data"
    export AMICONFIG_CONTEXT_URL="file:$LOCAL_USER_DATA"

    # Proper permissions
    chmod 0600 "$AMICONFIG_LOCAL_USER_DATA"

    # If we exit here, everything is consistent
    return 0
  fi

  # If we are here, no user-data has been found locally. Look for HTTP metadata
  $LOGGER "GCE: no local user-data found: trying metadata HTTP server $SERVER instead"

  # Remote check. Can we open a TCP connection to the server?
  nc -w 1 $SERVER 80 > /dev/null 2>&1
  if [ $? == 0 ] ; then
    $LOGGER "GCE: metadata server $SERVER seems to respond"
    LOCAL_USER_DATA="/var/lib/amiconfig/${GCE_API_VERSION}/"
    REMOTE_USER_DATA="${DEFAULT_URL}/cvm-user-data"
    DATA=$(wget --header="X-Google-Metadata-Request: True" -t$AMI_DOWNLOAD_RETRIES -T$AMI_DOWNLOAD_TIMEOUT_S -q -O - $REMOTE_USER_DATA 2> /dev/null)
    if [ $? == 0 ] ; then
      $LOGGER "GCE: user-data downloaded from $REMOTE_USER_DATA and written locally"

      # Write file there for script
      mkdir -p "$LOCAL_USER_DATA"
      echo "$DATA" | base64 -d > "$LOCAL_USER_DATA"/user-data
      chmod 0600 "$LOCAL_USER_DATA"/user-data

      # Export local location
      export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}/user-data"
      export AMICONFIG_CONTEXT_URL="file:$LOCAL_USER_DATA"

      # Exit consistently (user-data written, env exported, settings saved)
      return 0
    fi
  fi

  # Error condition (no env exported, no file written)
  $LOGGER "GCE: can't find any user-data"
  return 1

}


# Trying to retrieve user data from CloudStack. The user-data is saved locally.
# Returns 0 on success, 1 on failure
RetrieveUserDataCloudStack() {

  if [ ! -d /var/lib/dhclient ] ; then
    $LOGGER "CloudStack: can't find dhclient leases"
    return 1
  fi

  # Find the leases in every interface
  LEASES=$(ls -1 /var/lib/dhclient/*.leases)

  # Check if we are running a metadata server on the dhcp-identifier
  # specified on every interface
  for LEASE in $LEASES ; do
    SERVER=$( cat $LEASE | grep dhcp-server-identifier | tail -n1 )
    if [[ "$SERVER" =~ ([0-9.]+) ]] ; then

      SERVER=${BASH_REMATCH[1]}

      # Attempt a connection
      nc -w 1 $SERVER 80 > /dev/null 2>&1
      if [ $? == 0 ] ; then

        $LOGGER "CloudStack: metadata server $SERVER seems to respond"

        LOCAL_USER_DATA="/var/lib/amiconfig/latest/"
        REMOTE_USER_DATA="http://$SERVER/latest/"
        FOUND=0

        # We have a remote HTTP URL. Check if data is available locally
        if [ -s "${LOCAL_USER_DATA}user-data" ] ; then
          $LOGGER "CloudStack: local copy of user-data found, using it"
          FOUND=1
        else
          # Try to perform an HTTP GET request
          DATA=$(wget -t$AMI_DOWNLOAD_RETRIES -T$AMI_DOWNLOAD_TIMEOUT_S -q -O - $REMOTE_USER_DATA/user-data 2> /dev/null)
          if [ $? == 0 ] && [ ! -z "$DATA" ] ; then

            # Successful, update amiconfig
            $LOGGER "CloudStack: user-data found from $REMOTE_USER_DATA"

            # File is dumped there for running the script
            mkdir -p "$LOCAL_USER_DATA"
            echo "$DATA" > $LOCAL_USER_DATA/user-data

            FOUND=1
          fi
        fi

        # In case of success, update
        if [ $FOUND == 1 ] ; then

          # Fix permissions
          chmod 0600 "$LOCAL_USER_DATA"/user-data

          # Export local location
          export AMICONFIG_LOCAL_USER_DATA="${LOCAL_USER_DATA}user-data"

          # Pass remote URL there for metadata (used by amiconfig)
          echo "AMICONFIG_CONTEXT_URL=$REMOTE_USER_DATA" > $AMISETUP
          export AMICONFIG_CONTEXT_URL="$REMOTE_USER_DATA"

          # Exit consistently (user-data ok, env exported, settings saved)
          return 0

        fi

      else
        $LOGGER "CloudStack: metadata server $SERVER did not respond"
      fi

    fi
  done

  # Error condition (no file written, no env exported)
  $LOGGER "CloudStack: can't find any user-data"
  return 1
}

# Runs the initial shell script contained in user-data, if found. Returns 0 on
# success, 1 on failure. Return value of script is printed in log
RunUserDataScript() {

  # No download invloved here. Use local version
  $LOGGER "Using local copy of $AMICONFIG_CONTEXT_URL: found in $AMICONFIG_LOCAL_USER_DATA"

  TMP_USER_DATA=$(mktemp /tmp/amiconfig-user-data-XXXXX)

  # Strip white lines
  grep -v -e "^ *\$" "$AMICONFIG_LOCAL_USER_DATA" > $TMP_USER_DATA 2>&1

  # Empty file?
  if [ ! -s "$TMP_USER_DATA" ] ; then
    $LOGGER "No user-data available"
    rm -f "$TMP_USER_DATA"
    return 1
  fi

  # Check if it looks like a script
  if [ $(head -1 "$TMP_USER_DATA" | grep -c -e '^#!') == 0 ] ; then
    $LOGGER "user-data does not seem to contain a script, exiting gracefully"
    rm -f "$TMP_USER_DATA"
    return 0
  fi

  case $1 in
    before)
      sed -n '/#!.*sh.*before/,/^exit/p' $TMP_USER_DATA | sed  -e 's/\(#!.*\) \(.*\)/\1/' > "$TMP_USER_DATA".sh
      if [ -s "$TMP_USER_DATA".sh ] ; then
        awk '/#!.*sh/,/^$/ {print}' "$TMP_USER_DATA" > "$TMP_USER_DATA".sh
      else
        rm -f "$TMP_USER_DATA".sh
      fi
      rm -f "$TMP_USER_DATA"
    ;;

    after)
      sed -n '/#!.*sh\(.*after\|$\)/,/^exit/p' "$TMP_USER_DATA" | sed  -e 's/\(#!.*\) \(.*\)/\1/' > "$TMP_USER_DATA".sh
      if [ -s "$TMP_USER_DATA".sh ] ; then
        awk '/#!.*sh/,/^$/ {print}' "$TMP_USER_DATA" > "$TMP_USER_DATA".sh
      else
        rm -f "$TMP_USER_DATA".sh
      fi
      rm -f "$TMP_USER_DATA"
    ;;

    *)
      # Unknown option
      rm -f "$TMP_USER_DATA"
      return 1
    ;;
  esac

  if [ -f "$TMP_USER_DATA".sh ]; then
    $LOGGER "Running user-data [$1]"
    chmod +x "$TMP_USER_DATA".sh
    "$TMP_USER_DATA".sh 2>&1 | $PIPELOGGER
    $LOGGER "user-data script exit code: $?"
    rm -f "$TMP_USER_DATA".sh
  fi

  return 0
}

# The main function
Main() {

  # Assert amiconfig executable
  [ -f $AMICONFIG ] && [ -x $AMICONFIG ] || exit 1

  # Parse options
  FORCE='(none)'
  MODE='(none)'
  while [ $# -gt 0 ] ; do
    if [ "$1" == '--force' ] && [ "$FORCE" == '(none)' ] ; then
      FORCE=1
    elif [ "${1:0:1}" != '-' ] && [ "$MODE" == '(none)' ] ; then
      MODE="$1"
    fi
    shift
  done
  [ "$FORCE" == '(none)' ] && FORCE=0
  [ "$MODE" == '(none)' ] && MODE=''

  # Before doing anything, check if context has already been performed
  case "$MODE" in
    user)
      [ ! -e "$AMI_DONE_USER" ] && DO_CONTEXT=1
    ;;
    hepix)
      [ ! -e "$AMI_DONE_HEPIX" ] && DO_CONTEXT=1
    ;;
    *)
      $LOGGER "Invalid parameter. Usage: amiconfig.sh [user|hepix]"
      exit 2
    ;;
  esac

  if [ "$DO_CONTEXT" != 1 ] ; then
    if [ "$FORCE" == 1 ] ; then
      # Forcing
      $LOGGER "Contextualization for $MODE already run, forcing anyway as per explicit request"
    else
      # Don't recontextualize: exit now
      $LOGGER "Contextualization for $MODE already run, skipping (force with --force)"
      exit 0
    fi
  fi

  # Retrieve user-data. After calling this function, in case of success, we
  # have a consistent environment:
  #  - user-data, uncompressed, locally available at AMICONFIG_LOCAL_USER_DATA
  #  - remote path exported in AMICONFIG_CONTEXT_URL and saved in $AMISETUP
  #    (this is used by amiconfig, expecially to retrieve meta-data)
  RetrieveUserData
  if [ $? != 0 ] ; then
    $LOGGER "Can't retrieve any user data: aborting!"
    exit 1
  fi

  # Some debug
  $LOGGER "After retrieving user-data:"
  $LOGGER " * AMICONFIG_CONTEXT_URL=$AMICONFIG_CONTEXT_URL"
  $LOGGER " * AMICONFIG_LOCAL_USER_DATA=$AMICONFIG_LOCAL_USER_DATA"

  case "$MODE" in
    user)
      RunUserDataScript before
      $AMICONFIG 2>&1 #| $PIPELOGGER
      RunUserDataScript after
      mkdir -p `dirname "$AMI_DONE_USER"`
      touch "$AMI_DONE_USER"
    ;;
    hepix)
      $AMICONFIG -f hepix
      mkdir -p `dirname "$AMI_DONE_HEPIX"`
      touch "$AMI_DONE_HEPIX"
    ;;
  esac
}

#
# Entry point
#

Main "$@"
