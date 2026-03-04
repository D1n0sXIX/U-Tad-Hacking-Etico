# Modulo que printea resultados de los modulos de forma clara y organizada

# Funcion que muestra info de DetectorParametrosGet.py
def mostrar_resultados_parametros_get(parametros):
    if not parametros:
        return
    print("Parametros GET encontrados en la URL:")
    for clave, valor in parametros.items():
        print(f" - {clave} = {valor}")