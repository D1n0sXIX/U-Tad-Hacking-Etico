from bs4 import BeautifulSoup

# Modulo que detecta y separa los parametros GET de una URL
# booleano que indica si hay parametros GET en la URL
def hay_parametros_GET(url):
    # Comprobamos si la URL contiene un "?" que indica el inicio de los parametros GET
    if "?" in url:
        return True
    else:
        return False
    
# Funcion que separa los parametros GET de la URL y devuelve un diccionario
def separar_parametros_URL(url):
    # Creamos un diccionario para almacenar los parametros --> clave: valor
    parametros = {}
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

def sacar_parametros_html(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    enlaces = soup.find_all('a')
    enlaces_con_parametros = []  # ← lista que devolverás
    
    for enlace in enlaces:
        href = enlace.get('href', '')
        if hay_parametros_GET(href):
            parametros = separar_parametros_URL(href)
            # Añadimos el enlace y sus parametros a la lista de resultados
            enlaces_con_parametros.append({
            "href": href,
            "campos": parametros})
    
    return enlaces_con_parametros  

# Funcion principal - deteccion parametros GET
def obtener_Parametros_GET(response):
    # Extrae la URL de la respuesta
    url = response.url
    # Primero validamos si hay parametros GET en la URL, si no los hay, devolvemos un diccionario vacio
    if not hay_parametros_GET(url):
        print("No se han encontrado parametros GET en la URL")
        parametros_URL = {}
    else:
        parametros_URL = separar_parametros_URL(url)
    
    # Despues comrpobamos si hay parametros GET en el html de la pagina, si los hay, los añadimos al diccionario de parametros URL
    parametros_html = sacar_parametros_html(response)
    if not parametros_html:
        print("No se encontradon parametros GET en el HTML")

    return parametros_URL, parametros_html