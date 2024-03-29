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
        self.context = zmq.Context()
        self.socket_pub = self.context.socket(zmq.PUB)
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_sub.connect(f"tcp://{ro.HEALTHCHECK}:{ro.HEALTHCHECKOUTPORT}")
        self.socket_pub.connect(f"tcp://{ro.HEALTHCHECK}:{ro.HEALTHCHECKINPORT}")
        self.id = id
        self.medidasCorrectas = 0
        self.fallos = 0
        

        #Recibe mensajes de ping o de 
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"{self.id}")
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"all")
        
        self.tipo_monitor = tipo_monitor
        self.mediciones = []
        self.db_path = f"monitor_db/monitor{self.id}.json"
       
        print("Enviando solicitud de conexion")
        time.sleep(1)
        print("Solicitud enviada")
        self.socket_pub.send_string(f"{self.id}_connect")
        
        health = threading.Thread(target = self.healthCheck)
        health.start()
        self.correr()
    
    #Recibe y envia los mensajes del healthcheck
    def healthCheck(self):
        while True:
            mensaje: str = self.socket_sub.recv_string()
            print(mensaje)
            if "all" in mensaje:
                self.socket_pub.send_string(f"pong_{self.id}")
            
            elif "syncR" in mensaje and f"{self.id}" in mensaje:
                id_send: str = ""
                if "r" in self.id:
                    id_send = self.id.replace("r", "")
                else:
                    id_send = f"r{self.id}"
                self.socket_pub.send_string(f"{id_send}_db_{json.dumps(self.mediciones)}")
            
            elif "db" in mensaje:
                db = mensaje.split("_")[2]
                print("DB: ")
                print(db)
                self.mediciones = json.loads(db)
                f = open(self.db_path, "w")
                f.write(json.dumps(self.mediciones))
                f.close()

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
            print(f"Mensjae recibido (Desde intermediario): {mensaje}")

    def agregarMedicion(self, fecha: str, medicion: float, timestamp: float):
        context = zmq.Context()
        socket_pub_sc = context.socket(zmq.PUB)
    
        if float(medicion) < 0:
            socket_pub_sc.connect(f"tcp://{ro.SISTEMA_CALIDAD}:{ro.SISTEMA_CALIDADPORT}")
            time.sleep(0.2)
            print(f"Socket connected to tcp://*:{ro.SISTEMA_CALIDADPORT}")
            socket_pub_sc.send_string(f"Alerta generada: valor inválido {dt.datetime.now()}, sensor de {settings.tipos_sensor.get(self.tipo_monitor)}")
            self.fallos += 1
            return
        elif float(medicion) < float(settings.rangos_parametros_calidad.get(self.tipo_monitor)[0]) or float(medicion) > float(settings.rangos_parametros_calidad.get(self.tipo_monitor)[1]):
            socket_pub_sc.connect(f"tcp://{ro.SISTEMA_CALIDAD}:{ro.SISTEMA_CALIDADPORT}")
            time.sleep(0.2)
            print(f"Socket connected to tcp://*:{ro.SISTEMA_CALIDADPORT}")
            socket_pub_sc.send_string(f"Alerta generada: valor fuera de rango {dt.datetime.now()}, sensor de {settings.tipos_sensor.get(self.tipo_monitor)}")
        
        self.medidasCorrectas += 1
        print(f"Porcentaje de fallos: {self.darPorcentajeFallos()}")
        elapsedTime = time.time() - timestamp
        self.mediciones.append({"fecha" : fecha, "medicion" : medicion, "elapsedTime": elapsedTime})
        f = open(self.db_path, "w")
        jsonw = json.dumps(self.mediciones)
        f.write(jsonw)
        f.close()
        
    def darPorcentajeFallos(self):
        return round((self.fallos) / (self.fallos + self.medidasCorrectas), 2)
    

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
