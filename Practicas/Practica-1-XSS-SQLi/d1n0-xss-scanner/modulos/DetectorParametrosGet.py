# Modulo que detecta y separa los parametros GET de una URL

# booleano que indica si hay parametros GET en la URL
def hay_parametros_get(url):
    if "?" in url:
        print("Se han detectado parametros GET en la URL")
        return True
    else:
        print("No se han encontrado parametros GET en la URL.")
        return False
    
# Funcion que separa los parametros GET de la URL y devuelve un diccionario
def separar_parametros_get(url):
    # Creamos un diccionario para almacenar los parametros --> clave: valor
    parametros = {}
    # Si la URL tiene parametros GET
    if "?" in url:
        # Separamos la parte de la URL
        partes = url.split("?")
        # Si hay una algo despues del "?"
        if len(partes) > 1:
            # Los separamos por "&" y luego por "=" para obtener clave y valor
            parametros_str = partes[1]
            pares = parametros_str.split("&")
            # Para cada par clave-valor, los separamos por "=" y los almacenamos en el diccionario
            for par in pares:
                # Si el par contiene un "=", lo separamos en clave y valor, sino lo consideramos como una clave sin valor
                if "=" in par:
                    clave, valor = par.split("=", 1)
                    parametros[clave] = valor
    return parametros
# Ejemplo de diccionario resultado: {"id": "123", "search": "test"} <--> http://example.com/page?id=123&search=test

# Funcion principal - deteccion parametros GET
def parsear_parametros_URL(response):
    # Extrae la URL de la respuesta
    url = response.url
    # Primero comprobamos si hay parametros GET en la URL, si no los hay, devolvemos un diccionario vacio
    if not hay_parametros_get(url):
        return {}
    parametros = separar_parametros_get(url)
    return parametros