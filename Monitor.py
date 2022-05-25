from sys import argv
import zmq
import Routing as ro
import settings
import datetime as dt
from os.path import exists
import json
import time
import threading

import settings


class Monitor:
    tipo_monitor: int
    mediciones: list
    db_path: str
    id: str
    socket_pub: zmq.Socket
    socket_sub: zmq.Socket
    es_replica: bool

    def __init__(self, tipo_monitor, id:str) -> None:
        self.es_replica = not id.isnumeric()
        self.context = zmq.context()
        self.socket_pub = zmq.Socket(zmq.PUB)
        self.socket_sub = zmq.Socket(zmq.SUB)
        self.socket_sub.connect(f"tcp://{ro.HEALTHCHECK}:{ro.HEALTHCHECKSUBPORT}")
        self.socket_pub.connect(f"tcp://{ro.HEALTHCHECK}:{ro.HEALTHCHECKPUBPORT}")

        #Recibe mensajes de ping o de 
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"{self.id}")
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"all")
        
        self.tipo_monitor = tipo_monitor
        self.mediciones = []
        self.db_path = f"monitor_db/monitor{self.tipo_monitor}.json"
        self.id = id
        self.socket_pub.send_string(f"{self.id}-connect")

        health = threading.Thread(target = self.healthCheck)
        health.run()
        self.correr()

    #Recibe y envia los mensajes del healthcheck
    def healthCheck(self):
        while True:
            mensaje: str = self.socket_sub.recv_string()
            if "all" in mensaje:
                self.socket_pub.send_string(f"pong-{self.id}")
            
            elif f"syncR" in mensaje and f"{self.id}" in mensaje:
                self.socket_pub.send_string(f"{self.id}-db-{json.dumps(self.mediciones)}")
        

    def correr(self):
        if exists(self.db_path):
            f = open(self.db_path)
            archivo = f.read()
            if f != "":
                self.mediciones = json.loads(archivo)
            f.close()

        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.SUB)
        socket.connect(f"tcp://{ro.PROXYDIR}:{ro.PROXYOUTPORT}")
        socket.setsockopt_string(zmq.SUBSCRIBE, f"{settings.tipos_sensor.get(self.tipo_monitor)}=")

        while True:
            mensaje = socket.recv_string()
            mensaje = mensaje.replace(f"{settings.tipos_sensor.get(self.tipo_monitor)}=", "")
            mensaje_split = mensaje.split("_")
            self.agregarMedicion(str(dt.datetime.now()), mensaje_split[0], float(mensaje_split[1]))
            print(f"Mensjae recibido: {mensaje}")

    def agregarMedicion(self, fecha: str, medicion: float, timestamp: float):
        elapsedTime = time.time() - timestamp
        self.mediciones.append({"fecha" : fecha, "medicion" : medicion, "elapsedTime": elapsedTime})
        f = open(self.monitor_path, "w")
        jsonw = json.dumps(self.mediciones)
        f.write(jsonw)
        f.close()
    
    


def main():
    if len(argv) != 3:
        raise Exception("El numero de argumentos no es correcto")
    tipo_monitor = argv[1]
    if not tipo_monitor.isnumeric(): raise Exception("El tipo de monitor debe ser un numero")

    id = argv[2]
    if tipo_monitor != '0' and tipo_monitor !='1' and tipo_monitor !='2': raise Exception("El monitor debe corresponder a un tipo de sensor: 1. Temperatura, 2. PH, 3. Oxigeno")
    monitor = Monitor(int(tipo_monitor), id)

if __name__ == "__main__":
    main()
