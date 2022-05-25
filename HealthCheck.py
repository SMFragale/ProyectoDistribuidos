import zmq
import Routing as rt
import threading
import time

class HealthCheck:

    monitores: list
    check_list: list

    def __init__(self) -> None:
        self.context = zmq.Context()
        self.socket_pub = self.context.socket(zmq.PUB)
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_sub.bind(f"tcp://*:{rt.HEALTHCHECKINPORT}")
        self.socket_pub.bind(f"tcp://*:{rt.HEALTHCHECKOUTPORT}")

        self.monitores = []
        self.check_list = []
        pings = threading.Thread(target=self.ping)
        pings.start()
        self.correr()

    def ping(self):
        while True:
            if self.monitores:
                self.socket_pub.send_string("all-ping")
                for monitor in self.monitores:
                    if monitor not in self.check_list:
                        self.check_list.append(monitor)
                time.sleep(3)

    def correr(self):
        while True:
            mensaje: str = self.socket_sub.recv_string()
            print(mensaje)
            if "connect" in mensaje:
                id = mensaje.split("-")[0]
                if id not in self.monitores:
                    self.monitores.append(id)
                #Si se encuentra en el checklist, significa que el monitor se esta reconectando
                else:
                    id_send: str = ""
                    if "r" in id:
                        id_send = id.replace("r", "")
                    else:
                        id_send = f"{id}r"
                    self.socket_pub.send_string(f"{id_send}-syncR")
            elif "pong" in mensaje:
                monitor = mensaje.split("-")[1]
                self.check_list.remove(monitor)
            
            elif "db" in mensaje:
                self.socket_pub.send_string(mensaje)

monitor = HealthCheck()
