#!/bin/bash
# Macro para cada hora activar la bomba y esperar unos segundos para procesar las temperaturas de la placa y actualizarla 
# en la página web
curl "http://192.168.1.10/cm?cmnd=backlog%20Power%20on;delay%20100;power%20off"
sleep 30
sed -E s/\<b\>..../\<b\>`tail -20 /var/log/placa.log | grep tele/placa/SENSOR | tail -1 |cut -c 119-122`/ /mnt/f/index.html >/mnt/f/index.temp
mv /mnt/f/index.temp /mnt/f/index.html
python3 /home/hector/bin/funciones.py Temperatura
