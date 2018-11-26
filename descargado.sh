#!/bin/bash
sleep 3
mutt -s "Descargado fichero $1" Hector.D.Rguez@gmail.com <<FIN
Se ha descargado el fichero $1, $2
FIN
