#!/bin/bash
#set -x

_HOSTS=$($1/bin/jboss-cli.sh -c controller=$2:9999 --command=":read-children-names(child-type=host)"  | grep '        "' | sed 's/        \"//g' | sed 's/\",//g' | sed 's/"//g')

echo "HOSTS a revisar: " $_HOSTS
echo "$_HOSTS"|while read  _HOST
        do
            # descartamos al Domain Controller
            if [ "$_HOST" != "master" ]; then
                _SERVERS=$($1/bin/jboss-cli.sh -c controller=$2:9999 --command="/host=$_HOST:read-children-names(child-type=server)"  | grep '        "' | sed 's/        \"//g' | sed 's/\",//g' | sed 's/"//g' )
                 if [ "$_SERVERS" == "" ]; then
                   _SERVERS=$($1/bin/jboss-cli.sh -c controller=$2:9999 --command="/host=$_HOST:read-children-names(child-type=server)"  | grep result | cut -d '[' -f2 | sed 's/"//g' | sed 's/]//g')
                 fi
                echo "$_SERVERS"|while read _SERVER
                        do
                                echo "Servidor $_SERVER - Host $_HOST"
                                _STATUS=$($1/bin/jboss-cli.sh -c controller=$2:9999 --command="/host=$_HOST/server-config=$_SERVER:read-attribute(name=status)")
                                echo $_STATUS
                               #  echo -e "$(/opt/jboss-eap-dc/bin/jboss-cli.sh -c controller=161.131.236.135:9999 --command="/host=$_HOST/server=$_SERVER/subsystem=datasources/data-source=$_DS:test-connection-in-pool")"
                        done
            fi
        done
