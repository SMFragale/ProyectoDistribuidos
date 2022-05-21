import zmq
import Routing as ro

def main():
    context = zmq.Context()
    socket_sub: zmq.Socket = context.socket(zmq.SUB)
    socket_pub: zmq.Socket = context.socket(zmq.PUB)

    socket_sub.bind(f"tcp://*:{ro.PROXYINPORT}")
    socket_pub.bind(f"tcp://*:{ro.PROXYOUTPORT}")
    print(f"Socket de sub bound a tcp://*:{ro.PROXYINPORT}")
    socket_sub.setsockopt_string(zmq.SUBSCRIBE, f"")

    val = socket_sub.recv_string()
    print(f"Vlaor recobido: {val}")
    
    print("Recibio al menos uno")
    while (True):
        val = socket_sub.recv_string()
        print(f"Vlaor recobido: {val}")
        socket_pub.send_string(val)

if __name__ == "__main__":
    main()