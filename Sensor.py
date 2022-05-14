from sys import argv
from time import sleep
import zmq
import random

class Sensor:
    tipos_sensor = {
        0: "Temperatura",
        1: "PH",
        2: "Oxigeno"
    }

    rangos_parametros_calidad = {
        0: (68, 89),
        1: (6.0, 8.0),
        2: (2, 11)
    }

    tipo_sensor: int
    tiempoT: int
    archivo_conf: str

    prob_correcto: float
    prob_no_rango: float
    prob_error: float

    prendido: bool

    def __init__(self, tipo_sensor, tiempoT, archivo_conf) -> None:
        self.tipo_sensor = int(tipo_sensor)
        self.tiempoT = int(tiempoT)
        self.archivo_conf = archivo_conf
        self.leerArchivoConf()
        self.prendido = True
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
        socket.bind("tcp://*:5556")

        while self.prendido:
            prob_function = random.choices([self.producir_valor_valido, self.producir_valor_invalido, self.producir_error], weights=(self.prob_correcto*100, self.prob_no_rango*100, self.prob_error*100), k=1)[0]
            valor = prob_function()
            print(valor)
            socket.send_string(str(valor))
            sleep(self.tiempoT)

    
    def producir_valor_valido(self):
        return round(random.uniform(self.rangos_parametros_calidad.get(self.tipo_sensor)[0], self.rangos_parametros_calidad.get(self.tipo_sensor)[1]), 2)

    def producir_valor_invalido(self):
        return 0

    def producir_error(self):
        return -1

#Tipos de sensor: Temperatura: 0, PH: 1, Oxigeno: 2
#Formato de argumentos:
#tipo, tiempo, configuracion.txt
def main():
    if len(argv) != 4: raise Exception("Solo debe haber 3 argumentos en el sensor")

    tipo_sensor = argv[1]
    tiempoT = argv[2]
    archivo_conf = argv[3]

    tipo_valido = tipo_sensor == "0" or "1" or "2"
    if not tipo_valido: raise Exception("El tipo del sensor no es valido. Debe ser => Temperatura: 0, PH: 1, Oxigeno: 2")
    tiempo_valido = tiempoT.isnumeric() and int(tiempoT) > 0
    if not tiempo_valido: raise Exception("El argumento de tiempo debe ser un numero")
    archivo_valido = archivo_conf.endswith(".txt")
    if not archivo_valido: raise Exception("El nombre del archivo no es valido. Debe ser de tipo .txt")

    sensor = Sensor(tipo_sensor, tiempoT, archivo_conf)


if __name__ == "__main__":
    main()
