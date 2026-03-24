import string

# Funcion auxiliar que rehace la peticion segun el tipo de parametro
def obtener_respuesta(reflejado, session):
    if reflejado["tipo"] == "GET_URL" or reflejado["tipo"] == "GET_HTML":
        return session.get(reflejado["etiqueta"], params={reflejado["parametro"]: reflejado["token"]})
    elif reflejado["tipo"] == "POST":
        return session.post(reflejado["etiqueta"], data={reflejado["parametro"]: reflejado["token"]})
    return None

# Funcion que determina el contexto donde se refleja el token
def determinar_contexto(reflejado, session):
    response = obtener_respuesta(reflejado, session)
    if response is None:
        return "desconocido"
    index = response.text.find(reflejado["token"])
    if index == -1:
        return "desconocido"

    # Analizamos solo el fragmento ANTES del token
    fragmento_antes = response.text[index-50:index]
    
    if "<script" in fragmento_antes or "var " in fragmento_antes:
        return "javascript"
    elif "<!--" in fragmento_antes:
        return "comentario"
    elif ('="' in fragmento_antes or "='" in fragmento_antes) and ">" not in fragmento_antes.split('="')[-1]:
        return "atributo"
    else:
        return "html"
# Funcion principal - analiza el contexto de cada parametro reflejado
def analizar_contexto(parametros_reflejados, session):
    # Por cada parametro reflejado en el HTML
    for reflejado in parametros_reflejados:
        # Determinamos el contexto donde se refleja el token
        contexto = determinar_contexto(reflejado, session)
        # Añadimos el contexto al diccionario del parametro reflejado
        reflejado["contexto"] = contexto

        if reflejado["persistente"]:
            reflejado["tipo_xss"] = "stored"
        else:
            reflejado["tipo_xss"] = "reflected"

    return parametros_reflejados