# Sistema de medicion de calidad del agua 

## Ejecutar el Servidor
Para ejecutar el servidor es necesario [Python 3.6](https://www.python.org/downloads/release/python-360/) o mayor. 

Tambien es necesario tener la libreria ZeroMQ instalada 
```bash
pip install pyzmq
```

Una vez se cumple con ambos requisitos el sensor se puede ejecutar con:
```bash
python Sensor.py [tipo] [intervalo] [configuracion]
```
##### Nota: Si se tiene alguna otra versión de python instalada en el sistema, puede que sea necesario ejecutar el comando python3 en vez del comando python. 


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

### Ejemplo de ejecucion
```bash
python Sensor.py 1 5 sensconfig.txt
```

Este ejemplo ejecuta un sensor de PH que genera un nuevo valor cada 5 segundos y utiliza el archivo de configuracion sensconfig.txt ubicado en la raiz del proyecto.

Una vez ejecutado, el programa deberia responder
```bash
Sensor creado: tipo: PH, intervalo: 5 segundos, probabilidad de valor correcto: 0.6, probabilidad de valor fuera de rango: 0.3, probabilidad de error: 0.1
```
Seguido de los valores generados de acuerdo con el intervalo


## Ejecutar los Monitores.
### El Intermediario
Para ejecutar los monitores primero se necesita ejecutar el intermediario. Este programa se encarga de recibir las mediciones de los sensores y solo enviarlas a los monitores una vez se recibe una de cada tipo de medida.

Para ejecutar este programa intermedio se corre el comando.
```bash
python IntermediarioSubPub.py
```
La dirección donde se aloja este sistema debe indicarse en el campo PROXYDIR del archivo Rounting.py Adicionalmente se necesita indicar en este mismo archivo los puertos de entrada y salida de datos de este sistema en PROXYINPORT, PROXYOUTPORT


### El Sistema HealthCheck
Antes de ejecutar cualquier monitor, se necesita ejecutar el sistema HealthCheck. los monitores se suscriben a este sistema para poder revisar su funcionamiento continuo, si no se ejecuta este sistema primero, los monitores funcionarán, pero no tendrán ninguna garantía de uso.

El sistema HealthCheck envía constantemente mensajes de ping a los monitores para evidenciar que están activos. Si un monitor suscrito se cae, el peso de sus operaciones recae en su réplica. Cuando vuelve a activarse el monitor caído, el HealthCheck le pide a su réplica su base de datos y se la envía al Monitor para que no pierda información. 

Para ejecutar el sistema HealthCheck simplemente se ejecuta el comando.

```bash
python HealthCheck.py
```

### Los monitores
Una vez está en ejecución el sistema HealthCheck, se pueden ejecutar los monitores. Para ejecutarlos se requieren 2 parámetros:
- 1. El tipo de dato al cual se suscribe (el mismo de los sensores)
- 2. El id del monitor. Debe ser un número entero, si es una réplica debe tener el mismo id del monitor que está replicando acompañado de una 'r' al frente.
    - Ejemplo de id para un monitor: 1
    - Ejemplo de id para una réplica: r1

```bash
python Monitor.py 0 1
```
Este comando ejecuta un Monitor de temperatura (0) con id 1