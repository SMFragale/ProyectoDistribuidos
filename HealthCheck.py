<<<<<<< HEAD
from nis import cat
from warnings import catch_warnings
import zmq
import time
import Routing as rt
import threading

class HealthCheck:

    #Los SYNC son banderas que indican si un monitor estaba caido. De estarlo, la bandera se vuelve True
    monitor1_sync: bool
    monitor1_REP_sync: bool

    monitor2_sync: bool
    monitor2_REP_sync: bool

    monitor3_sync: bool
    monitor3_REP_sync: bool

    monitores: list

    monitor_table = {
        rt.MONITOR1 : rt.MONITOR1REP,
        rt.MONITOR1REP : rt.MONITOR1,

        rt.MONITOR2 : rt.MONITOR2REP,
        rt.MONITOR2REP : rt.MONITOR2,

        rt.MONITOR3 : rt.MONITOR3REP,
        rt.MONITOR3REP : rt.MONITOR3
    }

    def __init__(self) -> None:
        self.monitor1_sync = False
        self.monitor1_REP_sync = False
        self.monitor2_sync = False
        self.monitor2_REP_sync = False
        self.monitor3_sync = False
        self.monitor3_REP_sync = False

        self.monitores = [rt.MONITOR1, rt.MONITOR2, rt.MONITOR3, rt.MONITOR1REP, rt.MONITOR2REP, rt.MONITOR3REP]

        threading.Thread(target=self.ping)
        self.ping()

    def ping(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        while True:
            
            for monitor in self.monitores:
                socket.connect(f"tcp://{monitor}")
                try:
                    socket.send_string("ping")
                    message = socket.recv()
                    print(f"Monitor {monitor} respondio {message}")
                except:
                    if monitor == rt.MONITOR1:
                        print("El monitor 1 se encuentra caido")
                        self.monitor1_sync = True

                    elif monitor == rt.MONITOR2:
                        print("El monitor 2 se encuentra caido")
                        self.monitor2_sync = True

                    elif monitor == rt.MONITOR3:
                        print("El monitor 3 se encuentra caido")
                        self.monitor3_sync = True

                    elif monitor == rt.MONITOR1REP:
                        print("El monitor replica 1 se encuentra caido")
                        self.monitor1_REP_sync = True

                    elif monitor == rt.MONITOR2REP:
                        print("El monitor replica 2 se encuentra caido")
                        self.monitor2_REP_sync = True

                    elif monitor == rt.MONITOR3REP:
                        print("El monitor replica 3 se encuentra caido")
                        self.monitor3_REP_sync = True
            print()
            time.sleep(3)

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
        except:
            print(f"Error al sincronizar el monitor {monitor}, su replica esta caida")
        
        return None


monitor = HealthCheck()
=======
import zmq
import Routing as ro
import settings
import time

def main():
    print(type(time.time()))
    context = zmq.Context()
    socket_sub: zmq.Socket = context.socket(zmq.SUB)
    socket_pub: zmq.Socket = context.socket(zmq.PUB)
    socket_sub.bind(f"tcp://*:{ro.HCINPORT}")
    socket_pub.bind(f"tcp://*:{ro.HCOUTPORT}")



if __name__ == "__main__":
    main()
>>>>>>> 6a68eff5566f6b6e399ff1ac835cb5d42e3b2985
