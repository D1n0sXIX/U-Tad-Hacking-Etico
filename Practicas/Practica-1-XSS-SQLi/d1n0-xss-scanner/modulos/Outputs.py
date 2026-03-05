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

def mostrar_resultados_reflexion(parametros_reflejados):
    if not parametros_reflejados:
        print("No se han reflejado parametros GET o POST en la respuesta.")
        return

    print("Parametros reflejados encontrados:")
    for reflejado in parametros_reflejados:
        print(f" - Tipo: {reflejado['tipo']}")
        print(f"   Etiqueta: {reflejado['etiqueta']}")
        print(f"   Parametro: {reflejado['parametro']}")
        print(f"   Token: {reflejado['token']}")