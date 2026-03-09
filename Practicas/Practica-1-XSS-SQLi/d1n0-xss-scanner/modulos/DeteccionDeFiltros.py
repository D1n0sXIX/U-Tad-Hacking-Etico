# Modulo que propone variantes de payloads en funcion de los filtros detectados

# Los filtros mas comunes y que vamos a probar son:
# Bloqueo total → el carácter/palabra no aparece
# Codificación HTML → < → &lt;
# Codificación URL → < → %3C
# Eliminación → el carácter desaparece
# Case folding → SCRIPT → script o viceversa
# Truncado → el valor se corta a X caracteres

# Funcion que abre el fichero de filtros.txt y devuleve lalista de filtros que podemos usar
def cargarFiltros():
    with open("wordlists/filtros.txt", "r") as f:
        # Crea una lista con cada linea del fichero
        filtros = [linea.strip() for linea in f if linea.strip()]
    return filtros

def clasificar_filtro(filtro, response):
    match True:
        case _ if response.status_code in [403, 500]:
            return "bloqueado"
        case _ if filtro in response.text:
            return "aceptado"
        case _ if "&lt;" in response.text and "<" not in response.text:
            return "codificado_html"
        case _ if "%3C" in response.text and "<" not in response.text:
            return "codificado_url"
        case _ if filtro.lower() in response.text:
            return "lowercase"
        case _ if filtro.upper() in response.text:
            return "uppercase"
        case _:
            return "eliminado"

def probar_filtros(filtros, session, parametros_reflejados):
    # Para cada parametro reflejado, probamos cada filtro y clasificamos el resultado
    for parametro in parametros_reflejados:
        # Creamos un diccionario para almacenar los resultados de cada filtro en este parametro
        parametro["filtros"] = {}
        # Para cada filtro, hacemos una peticion y clasificamos el resultado
        for filtro in filtros:
            # Hacemos la peticion dependeindo del tipo de parametro
            if parametro["tipo"] == "GET_URL" or parametro["tipo"] == "GET_HTML":
                response = session.get(parametro["etiqueta"], params={parametro["parametro"]: filtro})
            elif parametro["tipo"] == "POST":
                response = session.post(parametro["etiqueta"], data={parametro["parametro"]: filtro})
            else:
                continue
            # Clasificamos el resultado y lo añadimos al diccionario
            parametro["filtros"][filtro] = clasificar_filtro(filtro, response)
    return parametros_reflejados

 
# Funcion que prueba cada filtro en cada parametro reflejado y añade una etiqueta al filtro
# Cada filtro puede tener la siguiente estructura:
    # aceptado → aparece tal cual
    # eliminado → desaparece completamente
    # bloqueado → la página no responde o devuelve error
    # codificado_html → < → &lt;
    # codificado_url → < → %3C
    # lowercase → SCRIPT → script
    # uppercase → script → SCRIPT
    # truncado → el valor se corta

def detectar_filtros(session, parametros_reflejados):
    filtros = cargarFiltros()
    parametros_reflejados = probar_filtros(filtros, session, parametros_reflejados)
    return parametros_reflejados