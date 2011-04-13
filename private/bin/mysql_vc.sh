#!/bin/bash

TMP_DIR=/tmp/mysql_vc
APP_BASELINE=applications/MYAPP/private/mysql/baseline.sql
APP_CHANGES=applications/MYAPP/private/mysql/changes.sql

script=${0##*/}
_u() { cat << EOF
usage: $script [options] db [path/to/commands.sql]

This script is used to create mysql schema files suitable for version control.
    -a      Web2py application
    -b      Create a baseline file at this location.
    -d      Run diff on baseline files.
    -k      Backup db (data and schema)
    -o      Options passed to mysql and mysqldump
    -od     Options passed only to mysqldump
    -om     Options passed only to mysql
    -p      Prompt for mysql password.
    -v      Verbose.
    -h      Print this help message.

EXAMPLE:
    $script db /path/to/commands.sql        # Run mysql commands in file to
                                                # update db
    $script -k /path/to/backup.out db       # Backup up db data and schema
    $script -d /path/to/baseline.sql db     # Diff db baseline with file
    $script -b /path/to/baseline.sql db     # Dump baseline to file.
    $script -o "-u root" db /path/to/commands.sql  # Pass options to mysql
    $script -a MYAPP                        # Update a web2py application

NOTES:
    With no options, a mysql command file argument is required. The script
    runs the commnds in a file and updates the database accordingly.

    If the -b baseline option is not provided, the baseline is dumped
    into a tmp file.

    With the -o options option, put multiple options in quotes.

    To continue running commands even if commands produce errors, use
    the mysql --force option. For example:

        $script -o "-u root --force" db /path/to/commands.sql

    If a password is required to access mysql, there are several ways of doing
    it. Using the -p password option is recommended.

        # This will prompt for password for every mysql command (not recommended)
        $script -o "-u root -p" db /path/to/commands.sql

        # This will prompt for password only once (recommended)
        $script -o "-u root" -p db /path/to/commands.sql

    With the -a application option, several default values are set. Values
    provided specifically on the command line take precedence. These two
    commands are equivalent.
        $script -a MYAPP
        $script -d $APP_BASELINE -k $TMP_DIR/MYAPP.out MYAPP $APP_CHANGES

EOF
}

__mi() { __v && echo -e "===: $*" ;}
__me() { echo -e "===> ERROR: $*" >&2; exit 1 ;}
__v()  { ${verbose-false} ;}

_options() {
    # set defaults
    args=()
    unset db
    unset commands
    unset app
    unset backup
    unset baseline
    unset diff
    unset options
    unset options_mysql
    unset options_mysqldump
    unset prompt
    unset verbose

    while [[ $1 ]]; do
        case "$1" in
            -a) shift; app=$1       ;;
            -b) shift; baseline=$1  ;;
            -d) shift; diff=$1      ;;
            -k) shift; backup=$1    ;;
            -o) shift; options=$1   ;;
            -od) shift; options_mysqldump=$1    ;;
            -om) shift; options_mysql=$1        ;;
            -p) prompt=1            ;;
            -v) verbose=true        ;;
            -h) _u; exit 0          ;;
            --) shift; [[ $* ]] && args+=( "$@" ); break;;
            -*) _u; exit 0          ;;
             *) args+=( "$1" )      ;;
        esac
        shift
    done

    [[ ! $app ]] && (( ${#args[@]} < 1 )) && { _u; exit 1; }
    [[ ! $app && ! $backup && ! $baseline && ! $diff ]] && ((${#args[@]} < 2)) && { _u; exit 1;}
    (( ${#args[@]} > 0 )) && db=${args[0]}
    (( ${#args[@]} > 1 )) && commands=${args[1]}
    [[ $app && ! $db ]] && db=$app
    [[ $app && $db == 'imdb' ]] && db='imdb_log'
    [[ $app && ! $commands ]] && commands=${APP_CHANGES//MYAPP/$app}
    [[ $app && ! $diff ]] && diff=${APP_BASELINE//MYAPP/$app}
    [[ ! $baseline && $diff ]] && mkdir -p $TMP_DIR && baseline=$(mktemp --tmpdir=$TMP_DIR)
}

_options "$@"

__v && __mi "Updating database: $db"

unset pw_option
if [[ $prompt ]]; then
    read -s -p "Enter mysql user password: " password
    pw_option="--password=$password"
fi

mysql_options="$options $options_mysql $pw_option"
mysqldump_options="$options $options_mysqldump $pw_option"

# Test and exit if fails. This will test the password and db.
mysql $mysql_options $db -e "" || exit 1

if [[ $backup ]]; then
    __v && __mi "Backing up $db to: $backup"
    mkdir -p ${backup%/*}
    mysqldump $mysqldump_options $db > $backup
fi

if [[ $commands ]]; then
    __v && __mi "Running commands in $commands"
    mysql $mysql_options $db < $commands
fi

if [[ $baseline ]]; then
    __v && __mi "Saving baseline of $db to: $baseline"
    mkdir -p ${baseline%/*}
    # Foreign keys cause foo if tables are not sourced in a specific order.
    # Turn off checks to prevent this.
    echo "/*!40101 SET foreign_key_checks = 0 */;" > "$baseline"
    mysqldump $mysqldump_options --compact --no-data $db | \
        sed 's/ AUTO_INCREMENT=[0-9]*\b//' | \
        awk '/^\/\*!40101/ {next} /^CREATE TABLE/ {print ""} {print}' \
        >> "$baseline"
    echo "/*!40101 SET foreign_key_checks = 1 */;" >> "$baseline"
fi

if [[ $diff ]]; then
    __v && __mi "Diff'ing baseline of $db with: $diff"
    diff -u $baseline $diff
fi
