# Health Check JBoss EAP Domain mode


## Preparar el ambiente de laboratorio, instalaremos 1 DC con 2 HC.

1. Crear 3 interfaces de red locales (reemplazar enp0s25 por eth0 o el nombre que corresponda a vuestro ambiente)

`sudo ifconfig enp0s25:1 192.168.0.69 netmask 255.255.255.0`  
`sudo ifconfig enp0s25:2 192.168.0.70 netmask 255.255.255.0`  
`sudo ifconfig enp0s25:3 192.168.0.71 netmask 255.255.255.0`  

El resultado debe ser del tipo:

$ ifconfig  
enp0s25: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500  
        ether 54:ee:75:52:b2:04  txqueuelen 1000  (Ethernet)  
        RX packets 0  bytes 0 (0.0 B)  
        RX errors 0  dropped 0  overruns 0  frame 0  
        TX packets 0  bytes 0 (0.0 B)  
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0  
        device interrupt 20  memory 0xb4a00000-b4a20000    
`

**enp0s25:1**: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500  
        **inet 192.168.0.69**  netmask 255.255.255.0  broadcast 192.168.0.255  
        ether 54:ee:75:52:b2:04  txqueuelen 1000  (Ethernet)  
        device interrupt 20  memory 0xb4a00000-b4a20000    

**enp0s25:2**: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500  
        **inet 192.168.0.70**  netmask 255.255.255.0  broadcast 192.168.0.255  
        ether 54:ee:75:52:b2:04  txqueuelen 1000  (Ethernet)  
        device interrupt 20  memory 0xb4a00000-b4a20000    

**enp0s25:3**: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500  
        **inet 192.168.0.71**  netmask 255.255.255.0  broadcast 192.168.0.255  
        ether 54:ee:75:52:b2:04  txqueuelen 1000  (Ethernet)  
        device interrupt 20  memory 0xb4a00000-b4a20000    

2. Instalación de 1 DC  
**Creamos directorios para nuestro ambiente en la ruta /opt/EAP-Ansible-POC**

`$ mkdir /opt/EAP-Ansible-POC`  
`$ mkdir /opt/EAP-Ansible-POC/domainController`  

**Instalamos nuestro EAP 6.4 sobre /opt/EAP-Ansible-POC/domainController**  
**Copiamos nuestra instalación para generar nuestros hosts controllers**  

`$ cp -R /opt/EAP-Ansible-POC/domainController /opt/EAP-Ansible-POC/hostController1`  
`$ cp -R /opt/EAP-Ansible-POC/domainController /opt/EAP-Ansible-POC/hostController2`  

**Configuramos nuestro DomainController para utilizar binding sobre enp0s25:1**  
`$ cp /opt/EAP-Ansible-POC/domainController/domain/configuration/host-master.xml /opt/EAP-Ansible-POC/domainController/domain/configuration/host.xml`  
`$ sed -i "s/127.0.0.1/192.168.0.69/g" /opt/EAP-Ansible-POC/domainController/domain/configuration/host.xml`

**Iniciamos nuestro Domain Controller**  
`$sh /opt/EAP-Ansible-POC/domainController/bin/domain.sh &`  

**Generamos usuario de administración:**  
name=poc  
pass=poc.Redhat123   
resultado --> \<secret value="cG9jLlJlZGhhdDEyMw=="/>

**Configuración cluster hornetQ para profile full-ha**  
`$ sh /opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh --connect controller=192.168.0.69:9999 -c "/profile=full-ha/subsystem=messaging/hornetq-server=default:write-attribute(name=cluster-user,value=poc)"`  
`$ sh /opt/EAP-Ansible-POC/domainController/bin/jboss-cli.sh --connect controller=192.168.0.69:9999 -c "/profile=full-ha/subsystem=messaging/hornetq-server=default:write-attribute(name=cluster-password,value=\"cG9jLlJlZGhhdDEyMw==\")`  

3. Instalación de 2 Hosts Controllers  
`$ cp /opt/EAP-Ansible-POC/hostController1/domain/configuration/host-slave.xml /opt/EAP-Ansible-POC/hostController1/domain/configuration/host.xml`  
`$ cp /opt/EAP-Ansible-POC/hostController2/domain/configuration/host-slave.xml /opt/EAP-Ansible-POC/hostController2/domain/configuration/host.xml`

**Configuramos nuestros Hosts Controllers para utilizar binding sobre enp0s25:2 y enp0s25:3 respectivamente**
`$ sed -i "s/127.0.0.1/192.168.0.70/g" /opt/EAP-Ansible-POC/hostController1/domain/configuration/host.xml`  
`$ sed -i "s/127.0.0.1/192.168.0.71/g" /opt/EAP-Ansible-POC/hostController2/domain/configuration/host.xml`

**Configuramos nustro jboss.domain.master.address**  
`$ sed -i "48i JAVA_OPTS=\"\$JAVA_OPTS -Djboss.domain.master.address=192.168.0.69\"" \/opt/EAP-Ansible-POC/hostController1/bin/domain.conf`   
`$ sed -i "48i JAVA_OPTS=\"\$JAVA_OPTS -Djboss.domain.master.address=192.168.0.69\"" \/opt/EAP-Ansible-POC/hostController2/bin/domain.conf`  

**Iniciamos los hosts controllers**  
`$ sh /opt/EAP-Ansible-POC/hostController1/bin/domain.sh &` 
`$ sh /opt/EAP-Ansible-POC/hostController2/bin/domain.sh &` 

**Seteamos el nombre del host**  
`$ sh /opt/EAP-Ansible-POC/hostController1/bin/jboss-cli.sh --connect controller=192.168.0.70:9999 -c "/host=$HOSTNAME:write-attribute(name=name,value=hostController1)"`  
`$ sh /opt/EAP-Ansible-POC/hostController2/bin/jboss-cli.sh --connect controller=192.168.0.71:9999 -c "/host=$HOSTNAME:write-attribute(name=name,value=hostController2)"`  

**Configuración autenticación sobre DomainController**  
`$ sh /opt/EAP-Ansible-POC/hostController1/bin/jboss-cli.sh --connect controller=192.168.0.70:9999 -c "/host=$HOSTNAME/core-service=management/security-realm=ManagementRealm/server-identity=secret:write-attribute(name=value, value=\"cG9jLlJlZGhhdDEyMw==\")"`  
`$ sh /opt/EAP-Ansible-POC/hostController2/bin/jboss-cli.sh --connect controller=192.168.0.71:9999 -c "/host=$HOSTNAME/core-service=management/security-realm=ManagementRealm/server-identity=secret:write-attribute(name=value, value=\"cG9jLlJlZGhhdDEyMw==\")"`   

`$ sh /opt/EAP-Ansible-POC/hostController1/bin/jboss-cli.sh --connect controller=192.168.0.70:9999 -c "/host=$HOSTNAME:write-remote-domain-controller(host="${jboss.domain.master.address}", port="${jboss.domain.master.port:9999}", security-realm="ManagementRealm", username=poc)"`  
`$ sh /opt/EAP-Ansible-POC/hostController2/bin/jboss-cli.sh --connect controller=192.168.0.71:9999 -c "/host=$HOSTNAME:write-remote-domain-controller(host="${jboss.domain.master.address}", port="${jboss.domain.master.port:9999}", security-realm="ManagementRealm", username=poc)"`  

**Reload de la configuración**  
`$ sh /opt/EAP-Ansible-POC/hostController1/bin/jboss-cli.sh --connect controller=192.168.0.70:9999 -c "/host=$HOSTNAME:reload"`  
`$ sh /opt/EAP-Ansible-POC/hostController2/bin/jboss-cli.sh --connect controller=192.168.0.71:9999 -c "/host=$HOSTNAME:reload"`  



# Ejecución HealthCheck Domain

1. Seteamos el listado de HostsControllers sobre fichero inventory/hostControllerList de la siguiente forma:  

192.168.0.70 ansible_connection=ssh ansible_ssh_user=root ansible_ssh_pass=poc  
192.168.0.71 ansible_connection=ssh ansible_ssh_user=root ansible_ssh_pass=poc  

**NOTA:** reemplazar "poc" por la password del usuario root.

2. Seteamos la ip del domain Controller en inventory/domainController de la siguiente forma:

192.168.0.69 ansible_connection=ssh ansible_ssh_user=root ansible_ssh_pass=poc

**NOTA:** reemplazar "poc" por la password del usuario root.

## Archivos importantes a tener en cuenta

1 SCRIPTS

**NOTA:** Para todos los script se debe modificarel path e ip del domain controlle  
**TODO:** Utilizar variables para scripts  

**datasources_list.sh** --> Entrega el listado completo de datasources del dominio    

**datasources_test_connection.sh** --> Realiza test connection de los datasources de todos los profiles del dominio, o bien sobre los profiles que se deseen revisar.  

**server_status** --> Revisa el estado de todos los servidores de dominio  

2. Ficheros YML

**healthcheck-eap-middleware.yml**  
En este fichero se definen las tareas que se ejecutarán sobre el domain controller y el órden de las mismas

**NOTA:** Reemplazar {{ansible_enp0s25_1.ipv4.address}} por la interfaz de red que corresponda

**healthcheck-eap-middleware.yml**  
En este fichero se definen las tareas que se ejecutarán sobre el listado de host controllers, principalmente son tareas de infraestructura  
**callback_plugins/json-custom.py**  
script python que define la ejecución de instrucciones, tareas y result para documentación.

3. Documentación  
**documentation/healthcheck.adoc**  
define los capítulos que se agregarán al documento de informe  

**documentation/variables.txt**  
define las variables del documento  
**documentation/chapters/** 
capítulos del documento. 
**NOTA:** estos capítulos deben ser editados antes de la generación del documento.

## Ejecución de health check y documentación

1. ejecución Healthcheck

`$ cd Ansible EAP HealthCheck/DomainMode`  
`$ ANSIBLE_COW_SELECTION=tux  ansible-playbook -i inventory/domaincontroller healthcheck-eap-middleware.yml`  
`$ ANSIBLE_COW_SELECTION=tux  ansible-playbook -i inventory/hostControllerList healthcheck-eap-rhel.yml`  

**NOTA:** la ejecuión de estos archivos generará como salida los ficheros ubicados en results/data

2. Ejecución Documentación
 
`$ cd Ansible EAP HealthCheck/DomainMode/documentation`  
`$ asciidoctor-pdf -b pdf healthcheck.adoc`

3. Revisar documento PDF generado
 












