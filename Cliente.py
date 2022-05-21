import zmq
import settings
import Routing as ro

context = zmq.Context()
socket: zmq.Socket = context.socket(zmq.SUB)

direccion: str
puerto: str

#direccion = input("Ingrese la direccion del sensor ")
#puerto = input("Ingrese el puerto del sensor ")

socket.connect(f"tcp://{ro.PROXYDIR}:{ro.PROXYOUTPORT}")
tipo = input("Ingrese el tipo de senor: \n")
tipo = int(tipo)
tipo_str = f"{settings.tipos_sensor.get(tipo)}"
if tipo_str == "None":
    tipo_str = "Temperatura"
socket.setsockopt_string(zmq.SUBSCRIBE, f"{tipo_str}=")
print(f"Subscribed to:  {tipo_str}=")
while(True):
    valor = socket.recv_string()
    print(f"Valor recibido: {valor}")