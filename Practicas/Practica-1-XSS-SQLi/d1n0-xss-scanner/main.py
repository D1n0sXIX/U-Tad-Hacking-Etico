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
#import requests # Para realizar peticiones HTTP

# Pruebas
def main():
    parser = argparse.ArgumentParser(description="Escaner de XSS automatizado")
    parser.add_argument("--url", required=True, help="URL objetivo")
    args = parser.parse_args()
    print(args.url)

if __name__ == "__main__":
    main()

