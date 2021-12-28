#!/bin/bash
# Macro para chequear si los procesos principales del sistema están funcionando y si no, arrancarlos.
function Amule {
	echo $(date) aMule parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
    sudo service amule-daemon stop
    pkill -9 amule
    sudo service amule-daemon start
    #amuled -c /mnt/e/.aMule/ -f
}    
# Generamos la lista de elementos a usar con un array 'asociativo' en bash
declare -A lista
lista=([transmission-da]='sudo service transmission-daemon start' [amuled]='sudo service amule-daemon restart' [vsftpd]='sudo service vsftpd start' [noip2]='sudo noip2' [minidlnad]='/usr/local/sbin/minidlnad')
# Ahora hacemos el bucle para comprobar los procesos
for f in "${!lista[@]}"
do
	pgrep -f $f
	if [ $? -eq 1 ]
	then
		echo $(date) $f cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		# Hay veces que casca el amuled pero no el amuleweb y por eso el servicio no arranca
		if [[ $f == amuled ]]
		then
			pkill -9 amule
		fi
		${lista[$f]}
	fi
done
# Hay un chequeo extra por el amule que algunas veces no desparece el proceso pero está inactivo
# Esperamos unos segundos a que arranque
#sleep 5
#tail -5 /mnt/e/.aMule/logfile|grep -e 'Todos los archivos' -e 'All PartFiles' -e 'Asio Sockets'
#if [ $? -eq 0 ]
#	then
#        tail -5 /mnt/e/.aMule/logfile >>/tmp/mulacaida.txt
#        Amule
#fi
# Y hay veces que sencillamente se queda frito sin dar ningún mensaje. Así que le hacemos hacer 
# algo para comprobar en el log que sigue vivo
amulecmd -c 'show dl'
if [[ $(tail -1 /mnt/e/.aMule/logfile|cut -c 13-16) != $(date|cut -c 17-20) ]]
    then
        echo $(tail -1 /mnt/e/.aMule/logfile|cut -c 13-16), $(date|cut -c 17-20)>>/tmp/mulacaida.txt
        Amule
fi
