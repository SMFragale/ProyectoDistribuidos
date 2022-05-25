from multiprocessing import context
from sys import argv
from turtle import rt
import zmq
import Routing as ro
import settings
import datetime as dt
from os.path import exists
import json

import settings


class Monitor:
    tipo_monitor: int
    mediciones: list
    db_path: str
    direccion: str

    def __init__(self, tipo_monitor, direccion) -> None:
        self.tipo_monitor = tipo_monitor
        self.mediciones = []
        self.db_path = f"monitor_db/monitor{self.tipo_monitor}.json"
        self.direccion = direccion
        self.wake()
        self.healthPing()

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
        socket.setsockopt_string(zmq.SUBSCRIBE, f"{settings.tipos_sensor.get(self.tipo_monitor)}")

        while True:
            mensaje = socket.recv_string()
            mensaje = mensaje.replace(f"{settings.tipos_sensor.get(self.tipo_monitor)}=", "")
            self.agregarMedicion(str(dt.datetime.now()), mensaje)
            print(mensaje)
    
    def agregarMedicion(self, fecha: str, medicion: float):
        self.mediciones.append({"fecha" : fecha, "medicion" : medicion})
        f = open(self.db_path, "w")
        jsonw = json.dumps(self.mediciones)
        f.write(jsonw)
        f.close()
    
    #Espera que el HealthCheck envie una solicitud de sync. Cuando la recibe, le envia al HealthCheck su base de datos
    def syncREP(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")

        while True:
            message = socket.recv()
            if message == "sync":
                print("Se recibio una solicitud de sincronizacion")
                socket.send_string(json.dumps(self.mediciones))

    def verificarValor(self):
        rangos_aceptables = settings.rangos_parametros_calidad.get(self.tipo_monitor)
    
    #Se llama cuando el monitor comienza a funcionar. Si el monitor estaba caido, la idea es que se sincronice con su replica
    def wake():
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{ro.HEALTHCHECKWAKE}")
        print("Se inicia el monitor")
        socket.send_string()


    #Debe ejecutarse en un Hilo para no estorbar el principal
    def healthPing(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5002")
        print("inicia el checkeo de pings")
        
        while True:
            ping = socket.recv()
            print(f"recibio {ping}")
            socket.send_string("Pong")


def main():
    if len(argv) != 3:
        raise Exception("El numero de argumentos no es correcto")
    tipo_monitor = argv[1]
    if not tipo_monitor.isnumeric(): raise Exception("El tipo de monitor debe ser un numero")
    if tipo_monitor != '0' and '1' and '2': raise Exception("El monitor debe corresponder a un tipo de sensor: 1. Temperatura, 2. PH, 3. Oxigeno")
    direccion = argv[2]
    monitor = Monitor(int(tipo_monitor))

if __name__ == "__main__":
    main()
