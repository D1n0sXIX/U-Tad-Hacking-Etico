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
    # Creamos lista con todos los parametros reflejados 
    reflejados = []
    # Iteramos sobre los parametros GET encontrados en la URL
    for parametro in parametros_get_URL:
        # Peticion con el token inyectado
        response = session.get(url, params={parametro: token})
        if token in response.text:
            # El token se refleja, ahora comprobamos si persiste
            # Hacemos una segunda peticion LIMPIA sin inyectar nada
            response_limpia = session.get(url)
            # Si el token sigue apareciendo sin haberlo enviado --> Stored XSS
            persistente = token in response_limpia.text
            reflejados.append({
                "tipo": "GET_URL",
                "etiqueta": url,
                "parametro": parametro,
                "token": token,
                "persistente": persistente
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
                response_limpia = session.get(href)
                persistente = token in response_limpia.text
                reflejados.append({
                    "tipo": "GET_HTML",
                    "etiqueta": href,
                    "parametro": parametro,
                    "token": token,
                    "persistente": persistente
                })
    return reflejados

def verificar_parametros_post(url, parametros_post, token, session):
    # Creamos una lista para almacenar los parametros reflejados
    reflejados = []
    # Iteramos sobre los formularios POST encontrados en la pagina
    for formulario in parametros_post:
        if formulario["action"].startswith("/"):
            url_post = url.split("/")[0] + "//" + url.split("/")[2] + formulario["action"]
        else:
            url_base = url.rsplit('/', 1)[0]
            url_post = url_base + '/' + formulario["action"]
        
        for campo in formulario["campos"]:
            response = session.post(url_post, data={campo: token})
            if token in response.text:
                response_limpia = session.post(url_post)
                persistente = token in response_limpia.text
                reflejados.append({
                    "tipo": "POST",
                    "etiqueta": url_post,
                    "parametro": campo,
                    "token": token,
                    "persistente": persistente
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