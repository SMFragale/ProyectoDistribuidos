import zmq
import Routing as rt
import threading
import time

class HealthCheck:

    socket_pub: zmq.Socket
    socket_sub: zmq.Socket

    monitores: list
    check_list: list

    def __init__(self) -> None:
        self.context = zmq.context()
        self.socket_pub = zmq.Socket(zmq.PUB)
        self.socket_sub = zmq.Socket(zmq.SUB)
        self.socket_sub.bind(f"tcp://*:{rt.HEALTHCHECKSUBPORT}")
        self.socket_pub.bind(f"tcp://*:{rt.HEALTHCHECKPUBPORT}")

        self.monitores = []
        self.check_list = []
        pings = threading.Thread(target=self.ping)
        pings.run()
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


    #Cuando un monitor hace wake() y su base de datos no esta sincronizada, esta funcion le pide su base de datos a la replica de dicho monitor para sincronizarlo
    def syncMonitor(self, monitor) -> str:
        synchronized = self.monitor_table.get(monitor)
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect(f"tcp://{synchronized}")
        try:
            socket.send_string("sync")
            db = socket.recv_string()
            socket.connect(f"tcp://{monitor}")
            socket.send_string(db)
        except:
            print(f"Error al sincronizar el monitor {monitor}, su replica esta caida")
        
        return None


monitor = HealthCheck()
