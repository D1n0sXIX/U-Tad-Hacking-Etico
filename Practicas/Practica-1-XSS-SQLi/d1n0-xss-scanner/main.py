# Analizar de Xss en Aplicaciones Web
# Autor: D1n0

# Flujo de Ejecuccion del Programa
# [1] Descubrimiento --> Detección de parametros GET + formularios POST en paralelo
#   - DeteccionParametrosGET.py
#   - DeteccionFormulariosPOST.py
# [2] Reflexión --> Envio de texto unico por cada entrada y comprobacion de si se refleja la respuesta
#  - VerificacionDeReflexion.py
# [3] Persistencia --> tras inyectar el codigo, realizar segunda peticion limpia para ver si la entrada persiste
#  - VerificacionDePersistencia.py
# [4] Contexto --> Determina DONDE se regleja el texto introducido, para adaptar el payload al contexto real
# - AnalisisDeContexto.py
# [5] Filtros --> identifica caracteres bloqueados/codificados y palabras prohibidas
#  - DeteccionDeFiltros.py
# [6] Evasión --> propone variantes de payloads en funcion de los filtros detectados
#  - TecnicasDeEvasion.py
# [7] Payloads --> contruir una lista de posibles payloads a inyectar en funcion del contexto y los filtros detectados
#  - GeneracionDePayloads.py
# [8] Output (transversal) --> Muestra  de forma clara los parametros potencialmente vulnerables, tipo de XSS y los payloads propuestos
# - Output.py


# Librerias e importaciones
import argparse # Para parsear argumentos de linea de comandos
import requests # Para realizar peticiones HTTP
from modules import DetectorParametrosGet
from modules import Outputs

def parsear_argumentos():
    parser = argparse.ArgumentParser(description="Escaner de XSS automatizado")
    parser.add_argument("--url", required=True, help="URL objetivo")
    args = parser.parse_args()
    return args.url

def crear_sesion():
    session = requests.Session()
    return session

def peticion_pagina(url, session):
    try:
        response = session.get(url)
        print("Peticion GET realizada con exito")
        print("Codigo de estado:", response.status_code)
        if response.status_code != 200:
            return None
        
        return response
    except requests.RequestException as e:
        print("\nAlgo ha fallado al realizar la peticion\nError:", e)
        return None

# Pruebas
def main():
    # Primeros pasos
    # Parsear argumentos de linea de comandos
    url = parsear_argumentos()
    print("Analizando :", url + "...\n")
    # Crear una sesion de requests para mantener cookies y cabeceras
    session = crear_sesion()

    # Hacer peticion GET de la pagina objetivo para obtener el contenido inicial
    response = peticion_pagina(url, session)
    if response is None:
        print("\nNo se pudo obtener la pagina objetivo.\nSaliendo...")
        return

    # [1] Descubrimiento GET
    parametros_get = DetectorParametrosGet.parsear_parametros_URL(response)
    Outputs.mostrar_resultados_parametros_get(parametros_get)
    
    # [2] Descubrimiento POST
    # [3] Reflexion
    # [4] Persistencia
    # [5] Contexto
    # [6] Filtros
    # [7] Evasion  
    return 0

if __name__ == "__main__":
    main()

