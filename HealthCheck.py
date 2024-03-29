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
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"")
        self.socket_sub.setsockopt

        self.monitores = []
        self.check_list = []
        pings = threading.Thread(target=self.ping)

        pings.start()
        self.correr()

    def ping(self):
        while True:
            if self.monitores:
                self.socket_pub.send_string("all_ping")
                for monitor in self.monitores:
                    if monitor not in self.check_list:
                        self.check_list.append(monitor)
                time.sleep(3)

    def correr(self):
        while True:
            print("Esperando mensaje")
            mensaje: str = self.socket_sub.recv_string()
            print(mensaje)
            if "connect" in mensaje:
                id = mensaje.split("_")[0]
                if id not in self.monitores:
                    self.monitores.append(id)
                #Si se encuentra en el checklist, significa que el monitor se esta reconectando
                else:
                    id_send: str = ""
                    if "r" in id:
                        id_send = id.replace("r", "")
                    else:
                        id_send = f"r{id}"
                    self.socket_pub.send_string(f"{id_send}_syncR")
            elif "pong" in mensaje:
                monitor = mensaje.split("_")[1]
                if monitor in self.check_list:
                    self.check_list.remove(monitor)
            
            elif "db" in mensaje:
                self.socket_pub.send_string(mensaje)

monitor = HealthCheck()
