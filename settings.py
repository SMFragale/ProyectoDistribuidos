class Colores:
        CORRECTO = '\033[92m'
        MAL_RANGO = '\033[93m'
        ERROR = '\033[91m'
        FIN = '\033[0m'

tipos_sensor = {
    0: "Temperatura",
    1: "PH",
    2: "Oxigeno"
}

rangos_parametros_calidad = {
    0: (68, 89) ,
    1: (6.0, 8.0),
    2: (2, 11)
}