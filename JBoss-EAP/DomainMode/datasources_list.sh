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
    if [ “$_DATASOURCE” == “” ]; then
       _DATASOURCES=$(/opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh -c controller=192.168.0.69:9999 --command="/profile=$_PROFILE/subsystem=datasources:read-children-names(child-type=data-source)" | grep result | sed 's/    \"result\" => \["//g' | sed 's/\"]//g')
    fi
    echo $_DATASOURCES
done
