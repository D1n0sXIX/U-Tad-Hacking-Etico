# d1n0-xss-scanner 🕷️

**Autor:** D1n0 (Alejandro Mamán) | INSO3A  
**Asignatura:** Hacking Ético  

---

## ¿Qué es esto?

Herramienta automatizada en Python para la detección y explotación de vulnerabilidades 
XSS (Cross-Site Scripting). Desarrollada como parte de la Práctica Tema 1.

Analiza una URL objetivo y de forma automática descubre puntos de inyección, 
verifica si el input se refleja, detecta filtros y genera payloads adaptados al contexto.

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
python main.py --url http://TARGET/xss/example1.php
```

---

## Estructura
```
d1n0-xss-scanner/
├── main.py
└── modulos/
    ├── DetectorParametrosGet.py
    ├── DetectorParametrosPost.py
    ├── VerificacionDeReflexion.py
    ├── VerificacionDePersistencia.py
    ├── AnalisisDeContexto.py
    ├── DeteccionDeFiltros.py
    ├── TecnicasDeEvasion.py
    ├── GeneracionDePayloads.py
    └── Outputs.py
```

---

## Entorno de pruebas

- Kali Linux
- Web for Pentesters (PentesterLab)
- Python 3.x