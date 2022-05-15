import zmq

context = zmq.Context()
socket: zmq.Socket = context.socket(zmq.SUB)

direccion: str
puerto: str

direccion = input("Ingrese la direccion del sensor ")
puerto = input("Ingrese el puerto del sensor ")

socket.connect(f"tcp://{direccion}:{puerto}")

socket.setsockopt_string(zmq.SUBSCRIBE, "Temperatura=")

while(True):
    valor = socket.recv_string()
    print(f"Valor recibido: {valor}")