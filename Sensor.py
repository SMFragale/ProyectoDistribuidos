from sys import argv
from time import sleep
import zmq
import random
import threading

class Sensor:

    class Colores:
        CORRECTO = '\033[92m'
        MAL_RANGO = '\033[93m'
        ERROR = '\033[91m'
        FIN = '\033[0m'

    tipos_sensor = {
        0: "Temperatura",
        1: "PH",
        2: "Oxigeno"
    }

    rangos_parametros_calidad = {
        0: (68, 89) ,
        1: (6.0, 8.0),
        2: (2, 11)
    }

    tipo_sensor: int
    tiempoT: int
    archivo_conf: str

    prob_correcto: float
    prob_no_rango: float
    prob_error: float

    running: bool
    prendido: bool

    puerto: str

    def __init__(self, tipo_sensor, tiempoT, archivo_conf, puerto) -> None:
        self.puerto = puerto
        self.tipo_sensor = int(tipo_sensor)
        self.tiempoT = int(tiempoT)
        self.archivo_conf = archivo_conf
        self.leerArchivoConf()
        self.prendido = True
        self.running = True
        print(f"Sensor creado: tipo: {self.tipos_sensor.get(self.tipo_sensor)}, intervalo: {str(self.tiempoT)} segundos, probabilidad de valor correcto: {self.prob_correcto}, probabilidad de valor fuera de rango: {self.prob_no_rango}, probabilidad de error: {self.prob_error}")
        self.correr()
    
    def leerArchivoConf(self):
        archivo = open(self.archivo_conf)
        contenido: str = archivo.readline()
        probabilidades = contenido.split(",")
        probabilidades = list(map(lambda prob: float(prob), probabilidades))
        self.prob_correcto = probabilidades[0]
        self.prob_no_rango = probabilidades[1]
        self.prob_error = probabilidades[2]

    def correr(self):
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.PUB)
        socket.bind(f"tcp://*:{self.puerto}")

        opciones = threading.Thread(target = self.options)
        opciones.start()

        while self.running:
            if self.prendido:
                prob_function = random.choices([self.producir_valor_valido, self.producir_valor_invalido, self.producir_error], weights=(self.prob_correcto*100, self.prob_no_rango*100, self.prob_error*100), k=1)[0]
                valor = prob_function()
                if prob_function == self.producir_valor_valido:
                    print(f"{self.Colores.CORRECTO}{valor}{self.Colores.FIN}")
                elif prob_function == self.producir_valor_invalido:
                    print(f"{self.Colores.MAL_RANGO}{valor}{self.Colores.FIN}")
                else:
                    print(f"{self.Colores.ERROR}{valor}{self.Colores.FIN}")
                socket.send_string(self.tipos_sensor.get(self.tipo_sensor) + "=" + str(valor))
                sleep(self.tiempoT)
        
    def options(self):
        while(self.running):
            command = input("")
            if command == "stop":
                self.prendido = False
                print("Se ha detenido el sensor")
            elif command == "run":
                print("El sensor continuara produciendo valores")
                self.prendido = True
            elif command == "kill":
                print("Se ha terminado la ejecucion")
                self.running = False

    
    def producir_valor_valido(self):
        return round(random.uniform(self.rangos_parametros_calidad.get(self.tipo_sensor)[0], self.rangos_parametros_calidad.get(self.tipo_sensor)[1]), 2)

    def producir_valor_invalido(self):
        return round(random.uniform(self.rangos_parametros_calidad.get(self.tipo_sensor)[1] + 1, 100), 2)

    def producir_error(self):
        return round(random.uniform(-100, -1), 2)

#Tipos de sensor: Temperatura: 0, PH: 1, Oxigeno: 2
#Formato de argumentos:
#tipo, tiempo, configuracion.txt
def main():
    if len(argv) != 5: raise Exception("Debe haber 4 argumentos en el sensor")

    tipo_sensor = argv[1]
    tiempoT = argv[2]
    archivo_conf = argv[3]
    puerto = argv[4]

    tipo_valido = tipo_sensor == "0" or "1" or "2"
    if not tipo_valido: raise Exception("El tipo del sensor no es valido. Debe ser => Temperatura: 0, PH: 1, Oxigeno: 2")
    tiempo_valido = tiempoT.isnumeric() and int(tiempoT) > 0
    if not tiempo_valido: raise Exception("El argumento de tiempo debe ser un numero")
    archivo_valido = archivo_conf.endswith(".txt")
    if not archivo_valido: raise Exception("El nombre del archivo no es valido. Debe ser de tipo .txt")
    if not puerto.isnumeric: raise Exception("El puerto debe corresponder a un numero")

    sensor = Sensor(tipo_sensor, tiempoT, archivo_conf, puerto)


if __name__ == "__main__":
    main()
