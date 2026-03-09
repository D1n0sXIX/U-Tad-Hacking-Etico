# Analizar de Xss en Aplicaciones Web
# Autor: D1n0

# Flujo de Ejecuccion del Programa
# [1] Descubrimiento --> Detección de parametros GET + formularios POST en paralelo
#   - DeteccionParametrosGET.py
#   - DeteccionFormulariosPOST.py
# [2] Reflexión --> Envio de texto unico por cada entrada y comprobacion de si se refleja la respuesta
#  - VerificacionDeReflexion.py
# [3] Persistencia --> tras inyectar el codigo, realizar segunda peticion limpia para ver si la entrada persiste
#  - VerificacionDeReflexion.py
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

from modulos import DetectorParametrosGet
from modulos import DetectorParametrosPost
from modulos import VerificacionDeReflexion
from modulos import AnalisisDeContexto
from modulos import DeteccionDeFiltros
from modulos import TecnicasDeEvasion
from modulos import GeneracionDePayloads
from modulos import Outputs
from time import sleep



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
    Outputs.separador()
    print("D1n0 XSS Scanner - XSS tester")
    # Creamos un diccionario apra almacenan Los tipos de XSS que podemos realizar
    tipos_xss = {"reflected": False, "stored": False,"dom": False}
    
    # Primeros pasos
    # Parsear argumentos de linea de comandos
    url = parsear_argumentos()
    print("Analizando :* " + url + " *")
    Outputs.separador()
    sleep(1) # Pausa de 1 segundo para mejorar la legibilidad

    # Crear una sesion de requests para mantener cookies y cabeceras
    session = crear_sesion()

    # Hacer peticion GET de la pagina objetivo para obtener el contenido inicial
    response = peticion_pagina(url, session)
    if response is None:
        print("\nNo se pudo obtener la pagina objetivo.\nSaliendo...")
        return

    Outputs.separador()
    # [1] Descubrimiento GET
    print("Analizando parametros GET...")
    parametros_get_URL, parametros_get_HTML = DetectorParametrosGet.obtener_Parametros_GET(response)
    Outputs.separador()
    sleep(1)
    if not parametros_get_URL and not parametros_get_HTML:
        print("No se han encontrado parametros GET")
    else:
        print("Resultados de parametros GET:")
        Outputs.mostrar_resultados_parametros_get_URL(parametros_get_URL) # Muestra los parametros GET encontrados en la URL
        Outputs.mostrar_resultados_parametros_get_HTML(parametros_get_HTML) # Muestra los enlaces con parametros GET encontrados en el HTML
    
    Outputs.separador()
    sleep(1)

    # [2] Descubrimiento POST
    parametros_post = DetectorParametrosPost.obtener_parametros_POST(response) # Devuelve una lista de diccionarios con los formularios POST encontrados
    Outputs.mostrar_resultados_parametros_post(parametros_post) # Muestra los formularios
    Outputs.separador()
    sleep(1)
    # [3] Reflexion [4] Persistencia y [5] Contexto
    if not parametros_get_URL and not parametros_get_HTML and not parametros_post:
        print("No se han encontrado parametros\nNo se puede hacer XSS")
        return
    
    print("Verificando reflexion de parametros GET y POST...")
    # primero verificamos la reflexion de los parametros GET encontrados en la URL, luego los del HTML y por ultimo los POST, para evitar hacer peticiones innecesarias a la pagina objetivo
    parametros_reflejados = VerificacionDeReflexion.verificar_reflexion(url, parametros_get_URL, parametros_get_HTML, parametros_post, session)
    # Despues analizamos el contexto de cada parametro reflejado para adaptar los payloads a corde
    parametros_reflejados = AnalisisDeContexto.analizar_contexto(parametros_reflejados, session) # Analiza el contexto de cada parametro reflejado
    Outputs.mostrar_resultados_analisis(parametros_reflejados) # Muestra los parametros reflejados encontrados
    Outputs.separador()
    sleep(1)
    # [6] Filtros
    # primero detectamos que filtros estan activos
    parametros_reflejados = DeteccionDeFiltros.detectar_filtros(session, parametros_reflejados)
    # luego mostramos los filtros encontrados
    Outputs.mostrar_filtros_encontrados(parametros_reflejados)
    Outputs.separador()
    sleep(1)

    # [7] Evasion y payloads
    parametros_reflejados = TecnicasDeEvasion.generar_payloads(parametros_reflejados)
    Outputs.mostrar_payloads_candidatos(parametros_reflejados)
    Outputs.separador()
    sleep(1)

    # [8] Output final
    parametros_reflejados = GeneracionDePayloads.generar_payloads(parametros_reflejados, session)
    Outputs.mostrar_payloads_exitosos(parametros_reflejados)

    Outputs.separador()
    print("Fin del analisis")
    return 0

if __name__ == "__main__":
    main()

