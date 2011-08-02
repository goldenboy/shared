#!/bin/bash

script=${0##*/}
_u() { cat << EOF
usage: $script path/to/script [args]

This script runs a 'python web2py.py' command.

All options are passed to the 'python web2py.py' command, in other words
as args to the -A, --args option.

EXAMPLE:
EOF
}

__mi() { __v && echo -e "===: $*" ;}
__me() { echo -e "===> ERROR: $*" >&2; exit 1 ;}
__v()  { ${verbose-false} ;}

_options() {
    # set defaults
    args=()
    unset script

    while [[ $1 ]]; do
        case "$1" in
             *) args+=( "$1" )  ;;
        esac
        shift
    done

    (( ${#args[@]} == 0 )) && { _u; exit 1; }
    script=${args[0]}
    unset args[0]
}

_options "$@"

__v && __mi "Starting:"

# Validate script
[[ ! -e "$script" ]] && __me "Invalid script. File not found: $script"

# Extract the app.
unset app
tmp_script=${script#*/}         # Strip 'applicaitons/'
app=${tmp_script%%/*}           # Strip 'private/bin/script.py'

python web2py.py --no-banner -L config.py -S "$app" -R "$script" -A ${args[*]}
