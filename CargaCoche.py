#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Para controlar la carga del coche en función de la batería que existe en 
	el sistema FV y también dependiendo del botón que haya sido apretado en 
	el SonOff Dual del garaje.
	Primer botón: Carga solamente de la FV dependiendo de un SOC mínimo
	Segundo botón: Carga de la FV y si no ha acabado, conmuta a la red 
	después de las 23 horas (pendiente de implementar)
"""

import time, os, datetime, sys, json, logging
import claves
import paho.mqtt.client as mqtt
from funciones import Log

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__("Entorno_" + sys.platform)
# Definimos una constante con las cadenas para preguntar por MQTT de manera que el códgio sea más legible
Preguntas = {
    "Batería": f"R/{claves.VictronInterna}/system/0/Dc/Battery/Soc",
    "SOCMínimo": "cmnd/CargaCoche/Mem2",
    "Relés": "cmnd/CargaCoche/STATUS",
}


class AccesoMQTT:
    """ Para acceder al Venus GX a través de MQTT de cara a gestionar la recarga del coche del sistema FV
	"""

    def __init__(self, debug=False):
        self.debug = debug
        # Creo el cliente
        self.client = mqtt.Client("Coche")
        # Conecto al broker
        self.client.connect("venus")
        # Asigno la función que va a procesar los mensajes recibidos
        self.client.message_callback_add(
            f"N/{claves.VictronInterna}/system/0/Dc/Battery/Soc", self.lee_Bateria
        )
        self.client.message_callback_add("stat/CargaCoche/STATUS", self.lee_EstadoDual)
        self.client.message_callback_add("stat/CargaCoche/RESULT", self.lee_Result)
        # Me subscribo a los tópicos necesarios, el SOC de la batería y el estado del relé
        self.client.subscribe(
            [
                (f"N/{claves.VictronInterna}/system/0/Dc/Battery/Soc", 0),
                ("stat/CargaCoche/#", 0),
            ]
        )
        # Comenzamos el bucle
        self.client.loop_start()
        # Inicializamos la variable que servirá para que no me mande más de un mensaje a la hora
        self.hora = 0
        self.rele1 = 0
        self.rele2 = 0
        self.SOCMinimo = 50
        # Obtenemos valores
        for f in Preguntas:
            self.pregunta(f)

    def lee_Bateria(self, client, userdata, message):
        """ Esta función es llamada para leer el estado de la batería
		"""
        # Lo importamos en formato json
        if self.debug:
            print(message.payload)
        # A veces recibimos mensajes vacíos, así que en ese caso ignoramos,
        # 	puesto que si no obtenemos un error en el json.loads()
        if len(message.payload.decode("utf-8")) == 0:
            return
        self.mensaje = json.loads(message.payload.decode("utf-8"))
        self.bateria = self.mensaje["value"]
        logging.debug(f"Bateria al {self.bateria}%, {self.mensaje}")
        if self.debug:
            print(f"Bateria al {self.bateria}%, {self.mensaje}")

    def lee_EstadoDual(self, client, userdata, message):
        """ Esta función es llamada para leer el estado de los Relés
		"""
        # Lo importamos en formato json
        self.mensaje = json.loads(message.payload.decode("utf-8"))
        if self.mensaje["Status"]["Power"] == 1 or self.mensaje["Status"]["Power"] == 3:
            self.rele1 = True
        else:
            self.rele1 = False
        if self.mensaje["Status"]["Power"] == 2 or self.mensaje["Status"]["Power"] == 3:
            self.rele2 = True
        else:
            self.rele2 = False
        logging.debug(f"Relé1 = {self.rele1}, Relé2 = {self.rele2}, {self.mensaje}")
        if self.debug:
            print(f"Relé1 = {self.rele1}, Relé2 = {self.rele2}, {self.mensaje}")

    def lee_Result(self, client, userdata, message):
        """ Esta función es llamada para leer el tanto el SOC Mínimo que tenemos que dejar en la batería
			como el estado de los relés cuando se activan o desactivan
		"""
        # Lo importamos en formato json
        self.mensaje = json.loads(message.payload.decode("utf-8"))
        if "Mem2" in self.mensaje:
            self.SOCMinimo = int(self.mensaje["Mem2"])
        if "POWER1" in self.mensaje:
            if self.mensaje["POWER1"] == "ON":
                self.rele1 = True
            else:
                self.rele1 = False
        if "POWER2" in self.mensaje:
            if self.mensaje["POWER2"] == "ON":
                self.rele2 = True
            else:
                self.rele2 = False
        if self.debug:
            print(
                f"SOC Mínimo {self.SOCMinimo}%, Relé1 = {self.rele1}, Relé2 = {self.rele2}, {self.mensaje}"
            )
        logging.debug(
            f"SOC Mínimo {self.SOCMinimo}%, Relé1 = {self.rele1}, Relé2 = {self.rele2}, {self.mensaje}"
        )

    def pregunta(self, que="Batería"):
        """ Manda la petición por MQTT, por defecto, del estado de la batería
		"""
        # Pedimos por MQTT lo solicitado
        self.client.publish(Preguntas[que], "")
        time.sleep(0.5)

    def controla(self):
        """ Controla el estado de la batería y del relé y activa o desactiva 
			en función de la hora y el % de SOC
		"""
        # Obtenemos los datos de estado de la batería
        self.pregunta()
        # Nos quedamos con la hora para no saturar de mensajes en la misma hora
        hora = datetime.datetime.now().hour
        mensaje = ""
        # Si está activo el relé, la batería está por debajo del 50% y son entre las 8 y las 23
        if self.rele1 and self.bateria <= self.SOCMinimo and hora > 8 and hora < 23:
            # Deberíamos de cortar la carga o pasar a la red, dependiendo de
            # 	lo que hayamos pedido
            # Esto lo controlaremos más adelante usando los dos botones que
            # 	nos ofrece el SonOff Dual para ponerlos externos, seguramente
            # 	en la carcasa del cuadro. Por ahora, solo cargamos de la FV
            self.client.publish("cmnd/CargaCoche/POWER1", "OFF")
            logging.info(f"Desconectamos el coche al {self.bateria}%")
            # Enviamos un mail comunicando el apagado si no lo hemos enviado antes
            if not hora == self.hora:
                os.system(
                    f'echo Desconectamos el coche |mutt -s "La batería está al {self.bateria}%" Hector.D.Rguez@gmail.com'
                )
                self.hora = hora
                mensaje = "y mandamos correo"
            logging.info(f"Batería al {self.bateria}%, desconectamos {mensaje}")
            Log(f"Batería al {self.bateria}%, desconectamos {mensaje}")
        # Si no está activo el relé y tenemos más del SOC Mínimo + un 10% adicional de batería,
        if (
            not self.rele1
            and self.bateria > self.SOCMinimo + 10
            and hora > 8
            and hora < 23
        ):
            # Volvemos a conectarlo
            self.client.publish("cmnd/CargaCoche/POWER1", "ON")
            if not hora == self.hora:
                os.system(
                    f'echo Conectamos el coche |mutt -s "La batería está al {self.bateria}%" Hector.D.Rguez@gmail.com'
                )
                self.hora = hora
                mensaje = "y mandamos correo"
            logging.info(f"Batería al {self.bateria}%, conectamos {mensaje}")
            Log(f"Batería al {self.bateria}%, conectamos {mensaje}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        debug = True
        nivel = logging.DEBUG
    else:
        debug = False
        nivel = logging.INFO
    # Inicializamos el logging
    logging.basicConfig(
        handlers=[logging.FileHandler("/tmp/Bateria.log"), logging.StreamHandler()],
        format="%(asctime)s %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        level=nivel,
    )
    # Inicializamos el objeto para acceder al MQTT
    victron = AccesoMQTT(debug)
    # Nos quedamos en bucle eterno controlando cada 2 minutos
    while True:
        victron.controla()
        time.sleep(120)
