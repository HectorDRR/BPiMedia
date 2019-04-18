#!/bin/bash
# Primero chequeamos si no ha cascado el proceso
pgrep transmission-da
if [ $? -eq 1 ]
	then
		echo $(date) transmission cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		#transmission-daemon -g /mnt/e/torrents/
		sudo service transmission-daemon start
		sleep 2
fi
pgrep amuled
if [ $? -eq 1 ]
	then
		echo $(date) aMule cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		pkill -9 amule
		#rm /mnt/e/.aMule/shareddir.dat
		#amuled -c /mnt/e/.aMule/ -f
		sudo service amule-daemon restart
		#sleep 10
		#compartidos
fi
# Si no es eso, chequeamos si se ha cerrado solo
tail -1 /mnt/e/.aMule/logfile|grep -e 'Todos los archivos' -e 'All PartFiles' -e 'Asio Sockets'
if [ $? -eq 0 ]
	then
		echo $(date) aMule parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo service amule-daemon stop
		sudo service amule-daemon start
		#pkill -9 amule
		#amuled -c /mnt/e/.aMule/ -f
fi
# Comprobamos también si está vivo el proceso del boton
pgrep python3
if [ $? -eq 1 ]
	then 
		echo $(date) Botón parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo screen -d -m -S Botones -h 20000 /home/hector/bin/boton.sh
fi
# Comprobamos el vsftpd
pgrep vsftpd
if [ $? -eq 1 ]
	then 
		echo $(date) VSFTPD parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo service vsftpd start
fi
# Comprobamos el noip2
pgrep noip
if [ $? -eq 1 ]
	then
		echo $(date) NOIP2 parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo noip2
fi
# Comprobamos el Minidlna
pgrep minidlna
if [ $? -eq 1 ]
	then
		echo $(date) Minidlnad parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		#/usr/local/sbin/minidlnad
		sudo service minidlnad start
fi
