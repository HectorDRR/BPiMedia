#! /bin/bash
# Macro para coprobar que están en funcionamiento los procesos básicos del sistema
for f in amuled transmiss minidlna smb vsftpd noip2 python3; do
	pgrep -a $f
	if [ $? -eq 1 ] 
		then
		echo Existe un problema con el proceso $f
		read p
	fi
done
