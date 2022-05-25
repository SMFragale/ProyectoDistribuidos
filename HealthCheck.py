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