# Sistema de medicion de calidad del agua 

## Ejecutar el Servidor
Para ejecutar el servidor es necesario [Python 3.6](https://www.python.org/downloads/release/python-360/) o mayor. 

Tambien es necesario tener la libreria ZeroMQ instalada 
```bash
pip install pyzmq
```

Una vez se cumple con ambos requisitos el sensor se puede ejecutar con:
```bash
python Sensor.py [tipo] [intervalo] [configuracion] [puerto]
```

Los 3 argumentos son obligatorios:
* tipo. Corresponde al tipo del sensor: 

    0: Sensor de temperatura

    1: Sensor de PH

    2: Sensor de oxigeno
* intervalo. Corresponde al intervalo de tiempo que tarda el sensor en generar un nuevo valor (en segundos)

* configuracion. Corresponde a el PATH a un archivo de configuracion que contiene la distribucion de probabilidad de los tipos de valores.

    Ej. sensconfig.txt
    
    ```txt
    0.6,0.3,0.1
    ```

    Como se puede ver la configuracion simplemente son 3 flotantes separados por comas que corresponden a:

    Probabilidad de un valor correcto, probabilidad de un valor fuera de rango, probabilidad de un valor erroneo.

    Respectivamente.

* puerto. El numero de puerto donde va a correr el sensor

### Ejemplo de ejecucion
```bash
python Sensor.py 1 5 sensconfig.txt 5556
```

Este ejemplo ejecuta un sensor de PH en el puerto 5556 que genera un nuevo valor cada 5 segundos y utiliza el archivo de configuracion sensconfig.txt ubicado en la raiz del proyecto.

Una vez ejecutado, el programa deberia responder
```bash
Sensor creado: tipo: PH, intervalo: 5 segundos, probabilidad de valor correcto: 0.6, probabilidad de valor fuera de rango: 0.3, probabilidad de error: 0.1
```
Seguido de los valores generados de acuerdo con el intervalo

## Ejecutar el Cliente de pruebas
Para ejecutar el cliente se requieren las mismas dependencias que el servidor, sin embargo no requiere argumentos.

```bash
python Cliente.py
```

El sensor sigue un patron PUBLISHER - SUBSCRIBER donde el publisher es el sensor y el subscriber es el Cliente. A futuro, el cliente sera reemplazado por los monitores