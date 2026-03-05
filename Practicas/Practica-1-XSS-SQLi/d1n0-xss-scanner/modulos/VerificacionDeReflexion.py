import random
import string
# Modulo que envia un texto unico por cada entrada y comprueba de si se refleja la respuesta

# Funcion que crea un token con el que vamos a ahcer testing
def crear_token_unico():
    # Generamos un string aleatorio de 6 caracteres (letras y numeros)
    aleatorio = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    # creamos el token unico
    tokenMagico = f"XSSD1n0s{aleatorio}XSSTest"
    return tokenMagico

#Verificamos si se reflejan los parametros GET en la URL
def verificar_parametros_url(url, parametros_get_URL, token, session):
    # Creamos una lista para almacenar los parametros reflejados
    reflejados = []
    # iteramos sobre los parametros GET encontrados en de la URL
    for parametro in parametros_get_URL:
        # Guardamos la respuesta
        response = session.get(url, params={parametro: token})
        # Comprobamos que este reflejada
        if token in response.text:
            # Si lo esta la guardamos en la lista de reflejados con su tipo, etiqueta y parametro
            reflejados.append({
                "tipo": "GET_URL",
                "etiqueta": url,
                "parametro": parametro,
                "token": token
            })
    return reflejados
# Funcion que verifica si se reflejan los parametros GET encontrados en el HTML
def verificar_parametros_html(parametros_get_HTML, token, session):
    # Creamos una lista para almacenar los parametros reflejados
    reflejados = []
    # Iteramos sobre los parametros GET encontrados en el HTML
    for enlace in parametros_get_HTML:
        # Guardamos el href del enlace y la respuesta de la peticion con el token inyectado en cada parametro
        href = enlace["href"]
        for parametro in enlace["campos"]:
            # Por cada parametro, hacemos una peticion con el token inyectado y comprobamos si se refleja en la respuesta
            response = session.get(href, params={parametro: token})
            # Si el token se refleja en la respuesta, lo guardamos en la lista de reflejados con su tipo, etiqueta y parametro
            if token in response.text:
                reflejados.append({
                    "tipo": "GET_HTML",
                    "etiqueta": href,
                    "parametro": parametro,
                    "token": token
                })
    return reflejados

def verificar_parametros_post(url, parametros_post, token, session):
    # Creamos una lista para almacenar los parametros reflejados
    reflejados = []
    # Iteramos sobre los formularios POST encontrados en la pagina
    for formulario in parametros_post:
        # MUY IMPORTANTE - Para hacer la peticion POST, necesitamos la URL del formulario, que se obtiene a partir de la URL de la pagina y el action del formulario
        url_base = url.rsplit('/', 1)[0]
        url_post = url_base + '/' + formulario["action"]
        # Por cada campo del formulario, hacemos una peticion POST con el token inyectado y comprobamos si se refleja en la respuesta
        for campo in formulario["campos"]:
            response = session.post(url_post, data={campo: token})
            # Si el token se refleja en la respuesta, lo guardamos en la lista de reflejados con su tipo, etiqueta y parametro
            if token in response.text:
                reflejados.append({
                    "tipo": "POST",
                    "etiqueta": url_post,
                    "parametro": campo,
                    "token": token
                })
    return reflejados

#Funcion princpal de este modulo, que devuelve una lista con los parametros reflejados si los tiene
def verificar_reflexion(url, parametros_get_URL, parametros_get_HTML, parametros_post, session):
    token = crear_token_unico()
    print("Token unico generado para testing:", token)
    
    parametros_reflejados = []
    parametros_reflejados += verificar_parametros_url(url, parametros_get_URL, token, session)
    parametros_reflejados += verificar_parametros_html(parametros_get_HTML, token, session)
    parametros_reflejados += verificar_parametros_post(url, parametros_post, token, session)
    
    return parametros_reflejados