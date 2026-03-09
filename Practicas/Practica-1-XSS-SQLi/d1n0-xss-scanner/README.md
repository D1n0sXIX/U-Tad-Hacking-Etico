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
    ├── TecnicasDeEvasion.py          # Selecciona payloads candidatos segun filtros detectados
    ├── GeneracionDePayloads.py       # Inyecta payloads y comprueba cuales se reflejan
    └── Outputs.py                    # Maneja toda la salida por terminal
```

---

## Flujo de ejecución

1. **Descubrimiento** → Detecta parámetros GET (URL + HTML) y formularios POST
2. **Reflexión** → Inyecta token único y verifica si se refleja en la respuesta
3. **Persistencia** → Comprueba si el token persiste sin inyectarlo (Stored XSS)
4. **Contexto** → Determina dónde se refleja: HTML, atributo, JavaScript o comentario
5. **Filtros** → Identifica caracteres y palabras bloqueadas o modificadas
6. **Evasión** → Selecciona payloads candidatos que evaden los filtros detectados
7. **Payloads** → Inyecta los candidatos y comprueba cuáles se reflejan sin modificar

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

---

## Comentarios del autor

Actualmente estimo que el programa funciona a un **~65%** de fiabilidad. La arquitectura y el flujo de detección están bien definidos, pero me faltan más entornos de prueba para pulir casos edge, mejorar la precisión del análisis de contexto y ampliar las wordlists. Con más testing en entornos variados el porcentaje debería subir considerablemente.

---

## Posibles mejoras futuras

- **Flag `--delay`** → Añadir pausa entre peticiones para no saturar el servidor objetivo
- **Flag `--domain-only`** → Filtrar enlaces HTML externos al dominio objetivo para evitar falsos positivos
- **Flag `--threads`** → Peticiones en paralelo para acelerar el análisis
- **Flag `--output`** → Exportar resultados a fichero JSON o HTML
- **Detección de path injection** → Detectar parámetros en la ruta de la URL (ej: `/buscar/VALOR`)
- **Mejora del análisis de contexto** → Detección más precisa de subcontextos JavaScript (dentro de string, función, etc.)
- **Wordlists ampliadas** → Añadir más payloads por contexto (atributo, JS, comentario) y más filtros a probar
- **Soporte para autenticación** → Flag `--cookie` para analizar páginas que requieren sesión activa
- **Filtrado de dominios externos** → Ignorar enlaces a redes sociales y dominios ajenos al objetivo
