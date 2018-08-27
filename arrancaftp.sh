#!/bin/bash
sudo tail -5 /var/log/vsftpd.log|grep 'FAIL DOWNLOAD'
if [ $? -eq 0 ]
	then
		echo $(date) VSFTP con problemas, lo arrancamos de nuevo>>/tmp/ftpcaido.txt
		sudo service vsftpd stop
		sudo rm /var/log/vsftpd.log
		sudo service vsftpd start
fi
