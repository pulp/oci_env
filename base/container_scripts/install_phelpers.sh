# The p-helper commands, back and better than ever!
# This file should be sourced to get the classic commands inside your oci-env


_paction() {
    SERVICES=$(s6-rc -d list | grep -E 'pulpcore|nginx' | paste -sd ' ')
    if  [ $# -gt 1 ] ; then
      SERVICES="${@:2}"
    fi
    echo "`setterm -foreground blue` s6-rc $1 ${SERVICES}"
    setterm -default
    s6-rc $1 ${SERVICES}
}

pstart() {
  _paction start $@
}
_pstart_help="Start all pulp-related services"

pstop() {
    _paction stop $@
}
_pstop_help="Stop all pulp-related services"

prestart() {
    _paction stop $@
    _paction start $@
}
_prestart_help="Restart all pulp-related services"

pstatus() {
    echo "`setterm -foreground green`Services that are live/ran successfully"
    _paction -a list
    echo "`setterm -foreground red`Services that are down"
    _paction -da list
}
_pstatus_help="Report the status of all pulp-related services"


pdbreset() {
    echo "Resetting the Pulp database"
    bash /opt/oci_env/base/container_scripts/database_reset.sh
}
_pdbreset_help="Reset the Pulp database"
# can get away with not resetting terminal settings here since it gets reset in phelp
_pdbreset_help="$_pdbreset_help - `setterm -foreground red -bold on`THIS DESTROYS YOUR PULP DATA"

pclean() {
    pdbreset
    sudo rm -rf /var/pulp/media/*
    redis-cli FLUSHALL
    pulpcore-manager collectstatic --clear --noinput --link
    if which mc ; then
      mc rb --force s3/${PULP_AWS_STORAGE_BUCKET_NAME}
      mc mb s3/${PULP_AWS_STORAGE_BUCKET_NAME}
    fi
}
_pclean_help="Restore pulp to a clean-installed state"
# can get away with not resetting terminal settings here since it gets reset in phelp
_pclean_help="$_pclean_help - `setterm -foreground red -bold on`THIS DESTROYS YOUR PULP DATA"

phelp() {
    # get a list of declared functions, filter out ones with leading underscores as "private"
    funcs=$(declare -F | awk '{ print $3 }'| grep -v ^_ | grep -v fzf)

    # for each func, if a help string is defined, assume it's a pulp function and print its help
    # (this is bash introspection via variable variables)
    for func in $funcs; do
        # get the "help" variable name for this function
        help_var="_${func}_help"
        # use ${!<varname>} syntax to eval the help_var
        help=${!help_var}
        # If the help var had a value, echo its value here (the value is function help text)
        if [ ! -z "$help" ]; then
            # make the function name easy to spot
            setterm -foreground yellow -bold on
            echo -n "$func"
            # reset terminal formatting before printing the help text
            # (implicitly format it as normal text)
            setterm -default
            echo ": $help"
        fi
    done

    # explicitly restore terminal formatting is reset before exiting function
    setterm -default
}
_phelp_help="Print this help"