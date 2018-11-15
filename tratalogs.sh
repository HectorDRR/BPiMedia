#!/bin/bash
# Comprimimos los logs que tenemos en /mnt/e/.mini
pushd /mnt/e/.mini
# Obtenemos la fecha de hoy
fecha=`date +%Y%m%d`
# Renombramos los ficheros
mv minidlna.log minidlna_$fecha.log
mv milog.txt milog_$fecha.txt
# Los pasamos al zip
zip -m logs.zip minidlna_$fecha.log milog_$fecha.txt
# Se acabó
popd
