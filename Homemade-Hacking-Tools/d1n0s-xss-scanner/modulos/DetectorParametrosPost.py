from bs4 import BeautifulSoup

# Recibe el objeto BeautifulSoup y devuelve el diccionario de parametros POST
def buscar_formularios_POST(soup):
    formularios_encontrados = []  # lista de formularios
    
    # Busca todos los formularios en la pagina
    formularios = soup.find_all('form')
    # Itera sobre los formularios encontrados y filtra los que son POST
    for formulario in formularios:
        # Si el formulario es POST, lo añadimos a la lista de formularios encontrados
        if formulario.get('method', '').lower() == 'post':
            # Creando el diccionario de este formulario
            form_dict = {
                "action": formulario.get('action', ''),
                "campos": {}
            }
            # Busca los inputs y rellenar form_dict["campos"]
            inputs = formulario.find_all('input')
            for input in inputs:
                nombre = input.get('name')
                valor = input.get('value', '')
                if nombre:
                    # Añadmios el campo al diccionario de campos del formulario
                    form_dict["campos"][nombre] = valor
            
            # Y añadimos form_dict a la lista de formularios encontrados
            formularios_encontrados.append(form_dict)
    
    return formularios_encontrados
    


# Parsea el HTML, llama a buscar_formularios_POST y devuelve el resultado
def obtener_parametros_POST(response):
    # Parsea el HTML de la respuesta con BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    # Busca formularios POST y devuelve un diccionario con los parametros encontrados
    parametros = buscar_formularios_POST(soup)

    ## Solo DEBUGGING
    ##print(soup.prettify())

    # Si no hay parametros POST
    if not parametros:
        print("No se han encontrado formularios POST en la pagina.")
    else:
        print("Se han encontrado formularios POST en la pagina.")
    return parametros




