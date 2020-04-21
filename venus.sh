# Macro para acceder al Venus GX y obtener datos de la instalación fotovoltaica
# Nos subscribimos al tópica que nos interesa, en este caso la producción de la FotoVoltaica
mosquitto_sub -h venus -t N/$Victron/pvinverter/32/Ac/Power -C 1 >/tmp/FV &
mosquitto_pub -h venus -t R/$Victron/pvinverter/32/Ac/Power -m ''
sleep .5
mosquitto_sub -h venus -t N/$Victron/battery/512/Soc -C 1 >/tmp/Bat &
mosquitto_pub -h venus -t R/$Victron/battery/512/Soc -m ''
sleep .5
