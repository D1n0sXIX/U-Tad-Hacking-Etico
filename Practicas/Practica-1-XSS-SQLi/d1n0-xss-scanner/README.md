# d1n0-xss-scanner 🕷️

**Autor:** D1n0 (Alejandro Mamán) | INSO3A  
**Asignatura:** Hacking Ético  

---

## ¿Qué es esto?

Herramienta automatizada en Python para la detección de vulnerabilidades 
XSS (Cross-Site Scripting). Desarrollada como parte de la Práctica Tema 1.

Analiza una URL objetivo y de forma automática descubre puntos de inyección, 
verifica si el input se refleja, analiza el contexto, detecta filtros y genera 
payloads adaptados al contexto.

---

## Instalación

```bash
git clone https://github.com/D1n0/d1n0-xss-scanner.git
cd d1n0-xss-scanner
pip install -r requirements.txt
```

---

## Uso

```bash
python main.py --url http://TARGET/xss/example1.php?name=hacker
```

---

## Estructura

```
d1n0-xss-scanner/
├── main.py
├── wordlists/
│   ├── filtros.txt       # Caracteres y palabras clave a probar
│   └── payloads.txt      # Payloads XSS organizados por contexto
└── modulos/
    ├── DetectorParametrosGet.py      # Detecta parametros GET en URL y HTML
    ├── DetectorParametrosPost.py     # Detecta formularios POST
    ├── VerificacionDeReflexion.py    # Verifica reflexion y persistencia del token
    ├── AnalisisDeContexto.py         # Determina el contexto de reflexion (html/js/atributo)
    ├── DeteccionDeFiltros.py         # Detecta filtros activos en la aplicacion
    ├── TecnicasDeEvasion.py          # Propone tecnicas de evasion segun filtros
    ├── GeneracionDePayloads.py       # Genera payloads adaptados al contexto
    └── Outputs.py                    # Maneja toda la salida por terminal
```

---

## Flujo de ejecución

1. **Descubrimiento** → Detecta parámetros GET (URL + HTML) y formularios POST
2. **Reflexión** → Inyecta token único y verifica si se refleja en la respuesta
3. **Persistencia** → Comprueba si el token persiste sin inyectarlo (Stored XSS)
4. **Contexto** → Determina dónde se refleja: HTML, atributo, JavaScript o comentario
5. **Filtros** → Identifica caracteres y palabras bloqueadas
6. **Evasión** → Propone variantes según los filtros detectados
7. **Payloads** → Genera lista de payloads adaptados al contexto y filtros

---

## Tipos de XSS detectados

- **Reflected XSS** → El input se refleja en la respuesta inmediata
- **Stored XSS** → El input persiste en el servidor sin reenviarlo
- **Path Injection** → La vulnerabilidad está en la ruta de la URL (PHP_SELF)

---

## Entorno de pruebas

- Kali Linux
- Web for Pentesters (PentesterLab) — ejemplos 1 al 8
- Python 3.x
