# Modulo que propone variantes de payloads en funcion de los filtros detectados

# Funcion que abre el fichero de filtros.txt y devuleve lalista de filtros que podemos usar
def cargarFiltros():
    with open("wordlists/filtros.txt", "r") as f:
        # Crea una lista con cada linea del fichero
        filtros = [linea.strip() for linea in f if linea.strip()]
    return filtros

def probar_filtros(filtros, session, parametros_reflejados):
    # TODO -> Toda la logica de probar filtros
    return filtros

def detectar_filtros(session, parametros_reflejados):
    filtros = cargarFiltros()
    filtros = probar_filtros(filtros, session, parametros_reflejados)
    return filtros