#!/bin/bash
#set -x

# Obtiene todos los profiles del domain
_PROFILES=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command=":read-children-names(child-type=profile)" | grep '        "' |sed 's/        \"//g'| sed 's/\"//g'|sed 's/,//g')

# o consultamos por los profiles que nos interesen
_PROFILES=default
echo "Profiles a revisar: " $_PROFILES

echo "$_PROFILES"|while read _PROFILE
 do
   echo "Obteniendo datasources para Profile " $_PROFILE
   _DATASOURCES=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/profile=$_PROFILE/subsystem=datasources:read-children-names(child-type=data-source)" | grep '        "' | sed 's/        \"//g' | sed 's/\",//g' | sed 's/"//g')

   #si _DATASOURCES está vacío se trata de ExampleDS
   if [ “$_DATASOURCES” == “” ]; then
       _DATASOURCES=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/profile=$_PROFILE/subsystem=datasources:read-children-names(child-type=data-source)" | grep result | sed 's/    \"result\" => \["//g' | sed 's/\"]//g')
   fi

   _HOSTS=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command=":read-children-names(child-type=host)"  | grep '        "' | sed 's/        \"//g' | sed 's/\",//g' | sed 's/"//g')

   echo "$_HOSTS"|while read  _HOST
        do
                _SERVERS=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/host=$_HOST:read-children-names(child-type=server)"  | grep '        "'| sed 's/        "//g' | sed 's/"//g' | sed 's/,//g')
                if [ “$_SERVER == “” ]; then
                  _SERVERS=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/host=$_HOST:read-children-names(child-type=server)"  | grep result | cut -d '[' -f2 | sed 's/"//g' | sed 's/]//g')
                fi
                echo "$_DATASOURCES"|while read _DS
                        do
                                  echo "$_SERVERS"|while read _SERVER
                                  do
                                    echo "Test Connection Host $_HOST, Servidor $_SERVER, Datasource $_DS"
                                    echo "/host="$_HOST"/server="$_SERVER"/subsystem=datasources/data-source="$_DS":test-connection-in-pool"
                                    echo -e "$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/host=$_HOST/server=$_SERVER/subsystem=datasources/data-source=$_DS:test-connection-in-pool")"
                                  done
                        done
        done
done
