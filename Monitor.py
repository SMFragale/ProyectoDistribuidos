from sys import argv


class Monitor:
    tipo_monitor: int

    def __init__(self, tipo_monitor) -> None:
        pass


def main():
    if len(argv) != 2:
        raise Exception("El numero de argumentos no es correcto")
    tipo_monitor = argv[1]
    if not tipo_monitor.isnumeric(): raise Exception("El tipo de monitor debe ser un numero")
    if tipo_monitor != '0' and '1' and '2': raise Exception("El monitor debe corresponder a un tipo de sensor: 1. Temperatura, 2. PH, 3. Oxigeno")
    monitor = Monitor(int(tipo_monitor))

if __name__ == "__main__":
    main()