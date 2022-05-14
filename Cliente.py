import sys
import zmq

context = zmq.Context()
socket: zmq.Socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5556")

socket.setsockopt_string(zmq.SUBSCRIBE, "")

while(True):
    valor = socket.recv_string()
    print(f"Valor recibido: {valor}")