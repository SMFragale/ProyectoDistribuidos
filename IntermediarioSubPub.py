import zmq
import Routing as ro
import settings

qTemp = []
qPH = []
qOx = []

def main():
    context = zmq.Context()
    socket_sub: zmq.Socket = context.socket(zmq.SUB)
    socket_pub: zmq.Socket = context.socket(zmq.PUB)

    socket_sub.bind(f"tcp://*:{ro.PROXYINPORT}")
    socket_pub.bind(f"tcp://*:{ro.PROXYOUTPORT}")
    print(f"Socket de sub bound a tcp://*:{ro.PROXYINPORT}")
    socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"")

    while (True):
        val = socket_sub.recv_string()
        print(f"Valor recibido: {val}")
        if val.startswith(settings.tipos_sensor.get(0)):
            qTemp.append(val)
        elif val.startswith(settings.tipos_sensor.get(1)):
            qPH.append(val)
        elif val.startswith(settings.tipos_sensor.get(2)):
            qOx.append(val)
        
        if(len(qTemp)>0 and len(qPH)>0 and len(qOx)>0):
            socket_pub.send_string(qTemp.pop())
            socket_pub.send_string(qPH.pop())
            socket_pub.send_string(qOx.pop())
            

if __name__ == "__main__":
    main()