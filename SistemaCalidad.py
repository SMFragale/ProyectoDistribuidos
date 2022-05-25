import json
import time

from sys import argv
import Routing as ro
import bcrypt
import zmq

class Sistema_calidad:

    user: str
    password: str
    def __init__(self, user, password) -> None:
        self.user = user
        self.password = password

        self.context = zmq.Context()
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_sub.bind(f"tcp://{ro.SISTEMA_CALIDAD}:{ro.SISTEMA_CALIDADPORT}")
        print(f"Socket connected to tcp://*:{ro.SISTEMA_CALIDADPORT}")
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"")

        self.correr()

    def correr(self):

        if not self.verificar_usuario():
            print("Usuario inválido")
            return 0

        while True:
            print("Esperando mensaje")
            time.sleep(3)
            mensaje: str = self.socket_sub.recv_string()
            print(mensaje)

    def cargar_datos(self, path, admin):
        with open(path) as contenido:
            users = json.load(contenido)

            for user in users:

                username = user.get('user')
                valido = user.get('valido')

                if(username == admin):
                    if(valido):
                        return username, valido, user.get('password')
        print("Error en los datos de entrada")


    def verificar_usuario(self):
        path = 'SistemaCalidad_db/Users.json'
        admin_info = self.cargar_datos(path, self.user)

        if( admin_info[1] != True):
            print("usuario invalido")
        else:
            password_2 = admin_info[2]
            password_2 = password_2.encode()

            sal = bcrypt.gensalt()

            pass_segura = bcrypt.hashpw(password_2, sal)

            password = self.password.encode()
            if bcrypt.checkpw(password, pass_segura):
                print("Usuario aceptado")
                return True
            else:
                print("Contraseña incorrecta")

        return False


if __name__ == "__main__":

    if len(argv) != 3:
        raise Exception("El número de argumentos no es correcto, SistemaCalidad.py  [usuario] [contraseña]")

    sistemaCalidad = Sistema_calidad(argv[1], argv[2])