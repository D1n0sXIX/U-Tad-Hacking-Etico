# Modulo que recibe filtros detectados y selecciona qué payloads de la lista son candidatos

# Funcion que carga payloads de un archivo de texto
def cargar_payloads():
    with open("wordlists/payloads.txt", "r") as f:
        payloads = [linea.strip() for linea in f if linea.strip()]
    return payloads

# Funcion que selecciona payloads candidatos en funcion de los filtros detectados
def seleccionar_payloads(parametros_reflejados, payloads):
    # Para cada parametro reflejado, comprobamos que payloads NO contienen elementos bloqueados
    for reflejado in parametros_reflejados:
        filtros = reflejado.get('filtros', {})
        #Los guardamos en una lista de candidatos, que luego añadiremos al diccionario del parametro reflejado
        candidatos = []
        # Por cada payload, comprobamos si contiene algun elemento bloqueado por los filtros detectados
        for payload in payloads:
            # Comprobar si el payload contiene algo bloqueado
            es_valido = True
            for elemento, resultado in filtros.items():
                if resultado in ["eliminado", "bloqueado"] and elemento in payload:
                    es_valido = False
                    break
            if es_valido:
                candidatos.append(payload)
        reflejado["payloads_candidatos"] = candidatos
    return parametros_reflejados


def generar_payloads(parametros_reflejados):
    payloads = cargar_payloads()
    return seleccionar_payloads(parametros_reflejados, payloads)