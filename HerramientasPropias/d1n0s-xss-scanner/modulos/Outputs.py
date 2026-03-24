# Modulo que printea resultados de los modulos de forma clara y organizada

# Funcion que solo hace más legible la impresion por terminal
def separador():
    print("\n" + "="*50 + "\n")

# Funcion que muestra info de DetectorParametrosGet.py
def mostrar_resultados_parametros_get_URL(parametros):
    if not parametros:
        return
    print("En la URL:")
    for clave, valor in parametros.items():
        print(f" - {clave} = {valor}")
    
def mostrar_resultados_parametros_get_HTML(parametros):
    if not parametros:
        return
    print("En el HTML:")
    for enlace in parametros:
        print(f" - {enlace['href']}")
        print("   Campos:")
        for campo, valor in enlace['campos'].items():
            print(f"     - {campo} = {valor}")

def mostrar_resultados_parametros_post(parametros):
    if not parametros:
        return
    print("Formularios POST encontrados en la pagina:")
    for formulario in parametros:
        print(f" - Action: {formulario['action']}")
        print("   Campos:")
        for campo, valor in formulario['campos'].items():
            print(f"     - {campo} = {valor}")

def mostrar_resultados_analisis(parametros_reflejados):
    if not parametros_reflejados:
        print("No se han reflejado parametros GET o POST en la respuesta.")
        return

    print("Parametros reflejados encontrados:")
    for reflejado in parametros_reflejados:
        print(f" - Tipo: {reflejado['tipo']}")
        print(f"   Etiqueta: {reflejado['etiqueta']}")
        print(f"   Parametro: {reflejado['parametro']}")
        print(f"   Token: {reflejado['token']}")
        print(f"   Tienen persistencia: {'Si' if reflejado['persistente'] else 'No'}")
        print(f"   Contexto: {reflejado['contexto']}")
        print(f"   Tipo de XSS: {reflejado['tipo_xss']}")

def mostrar_filtros_encontrados(parametros_reflejados):
    print("Filtros encontrados en los parametros reflejados:")
    for reflejado in parametros_reflejados:
        print(f" - Parametro: {reflejado['parametro']} ({reflejado['tipo']})")
        print("   Filtros:")
        for filtro, resultado in reflejado["filtros"].items():
            if resultado != "aceptado":
                print(f"     - {filtro}: {resultado}")

def mostrar_payloads_candidatos(parametros_reflejados):
    print("Posibles payloads candidatos para cada parametro reflejado:")
    for reflejado in parametros_reflejados:
        print(f" - Parametro: {reflejado['parametro']} ({reflejado['tipo']})")
        print("   Payloads candidatos:")
        for payload in reflejado.get("payloads_candidatos", []):
            print(f"     - {payload}")

def mostrar_payloads_exitosos(parametros_reflejados):
    for reflejado in parametros_reflejados:
        print(f" - Parametro: {reflejado['parametro']} ({reflejado['tipo']})")
        exitosos = reflejado.get("payloads_exitosos", [])
        candidatos = reflejado.get("payloads_candidatos", [])
        
        if not candidatos:
            print("   No hay payloads candidatos - actualiza wordlists/payloads.txt")
        elif not exitosos:
            print("   Ningún payload se reflejó sin modificar - prueba a actualizar wordlists/payloads.txt")
        else:
            print("   Payloads exitosos:")
            for payload in exitosos:
                print(f"     - {payload}")