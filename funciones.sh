#!/bin/bash
function procesos {
	# Comprueba la existencia de los procesos normales del sistema
	for f in amuled transmiss minidlna smb vsftpd noip2 python3; do
        	pgrep -a $f
        	if [ $? -eq 1 ]
                	then
                	echo Existe un problema con el proceso $f
                	read p
        	fi
	done
}
function Series {
	# Lista las series pendientes de pasar a disco
	find /mnt/e/pasados/ -type f -perm -u+rwx -exec du -ch '{}' +|sort -k 2|more
}
function json {
	# Extrae de una cadena JSON tipo {"item": valor} el valor
	echo ${1:`expr index "$1" :`:-1}
}
function Estado_Placa {
	# Si hay fichero de log, extraemos la temperatura de allí, si no, la pedimos directamente a la placa.
	Placa=Off
	if [ -f /var/log/placa.log ]; then
		ACS=$(tail /var/log/placa.log |grep SENSOR|tail -1)
		ACS="${ACS#*\"Temperature\":}"
		ACS=${ACS:0:4}
		#ACS=$(tail /var/log/placa.log |grep SENSOR|tail -1 |cut -c 132-135)
		[[ "$(tail /var/log/placa.log|grep placa/STATE|tail -1)" = *"ON"* ]] && Placa=On
	fi
	if [ ${#ACS} -eq 0 ]; then	
		ACS=$(curl -s http://placa/cm?cmnd=Status%2010)
		ACS="${ACS#*\"Temperature\":}"
		ACS=${ACS:0:4}
		[[ "$(curl -s http://placa/cm?cmnd=Status)" = *"ON"* ]] && Placa=On
	fi
	echo \{\"ACS\":$ACS\}>/mnt/f/ACS.txt
}