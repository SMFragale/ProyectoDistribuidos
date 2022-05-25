from distutils import archive_util
from sys import argv
from numpy import longlong
import zmq
import Routing as ro
import settings
import datetime as dt
from os.path import exists
import json
import time

import settings


class Monitor:
    tipo_monitor: int
    mediciones: list
    monitor_path: str

    def __init__(self, tipo_monitor) -> None:
        self.tipo_monitor = tipo_monitor
        self.mediciones = []
        self.monitor_path = f"monitor_db/monitor{self.tipo_monitor}.json"
        self.correr()

    def correr(self):
        if exists(self.monitor_path):
            f = open(self.monitor_path)
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

    def verificarValor(self):
        rangos_aceptables = settings.rangos_parametros_calidad.get(self.tipo_monitor)

def main():
    if len(argv) != 2:
        raise Exception("El numero de argumentos no es correcto")
    tipo_monitor = argv[1]
    if not tipo_monitor.isnumeric(): raise Exception("El tipo de monitor debe ser un numero")
    if tipo_monitor != '0' and tipo_monitor !='1' and tipo_monitor !='2': raise Exception("El monitor debe corresponder a un tipo de sensor: 1. Temperatura, 2. PH, 3. Oxigeno")
    monitor = Monitor(int(tipo_monitor))

if __name__ == "__main__":
    main()
