#!/bin/bash
# Primero chequeamos si no ha cascado el proceso
pgrep transmission-da
if [ $? -eq 1 ]
	then
		echo $(date) transmission cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		transmission-daemon -g /mnt/e/torrents/
		sleep 2
		exit
fi
pgrep amuled
if [ $? -eq 1 ]
	then
		echo $(date) aMule cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		pkill -9 amule
		rm /mnt/e/.aMule/shareddir.dat
		amuled -c /mnt/e/.aMule/ -f
		sleep 10
		compartidos
		exit
fi
# Si no es eso, chequeamos si se ha cerrado solo
tail -1 /mnt/e/.aMule/logfile|grep 'Todos los archivos'
if [ $? -eq 0 ]
	then
		echo $(date) aMule parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		#sudo service amule-daemon stop
		#sudo service amule-daemon start
		pkill -9 amule
		amuled -c /mnt/e/.aMule/ -f
fi
# Comprobamos también si está vivo el proceso del boton
pgrep python3
if [ $? -eq 1 ]
	then 
		echo $(date) Botón parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo screen -d -m -S Botones -h 20000 /home/hector/bin/boton.sh
fi
