# Modulo que inyecta los payloads candidatos y comprueba cuales se reflejan sin modificar

# Si el payload se refleja sin modificar, lo añadimos a la lista de payloads exitosos para ese parametro reflejado
def inyectar_payload(parametro, payload, session):
    if parametro["tipo"] == "GET_URL" or parametro["tipo"] == "GET_HTML":
        return session.get(parametro["etiqueta"], params={parametro["parametro"]: payload})
    elif parametro["tipo"] == "POST":
        return session.post(parametro["etiqueta"], data={parametro["parametro"]: payload})
    return None
# Funcion que inyecta los payloads candidatos y comprueba cuales se reflejan sin modificar
def probar_payloads(parametros_reflejados, session):
    # recorremos cada parametro reflejado
    for reflejado in parametros_reflejados:
        reflejado["payloads_exitosos"] = []
        # para cada payload candidato
        for payload in reflejado.get("payloads_candidatos", []):
            # hacemos una peticion donde inyectamos el payload y comprobamos si se refleja sin modificar
            response = inyectar_payload(reflejado, payload, session)
            #Si el payload se refleja sin modificar, lo añadimos a la lista de payloads exitosos
            if response and payload in response.text:
                reflejado["payloads_exitosos"].append(payload)

    return parametros_reflejados
# Funcion main llama a probar_payloads
def generar_payloads(parametros_reflejados, session):
    return probar_payloads(parametros_reflejados, session)