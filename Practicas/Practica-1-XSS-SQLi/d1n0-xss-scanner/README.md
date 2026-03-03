# XSS Scanner 🕷️

Herramienta automatizada en Python para la detección y explotación de vulnerabilidades 
XSS (Cross-Site Scripting) sobre los 8 primeros niveles de Web for Pentesters (PentesterLab).

---

## Instalación

Clona el repositorio e instala las dependencias:

git clone https://github.com/tuusuario/xss-scanner.git
cd xss-scanner
pip install -r requirements.txt

---

## Uso

python main.py --url http://192.168.1.100/xss/example1.php

---

## Estructura

xss_scanner/
├── main.py
└── modules/
    ├── DetectorParametrosGet.py
    ├── DetectorFormulariosPost.py
    ├── VerificacionDeReflexion.py
    ├── VerificacionDePersistencia.py
    ├── AnalisisDeContexto.py
    ├── DeteccionDeFiltros.py
    ├── TecnicasDeEvasion.py
    ├── GeneracionDePayloads.py
    └── Outputs.py

---

## Entorno de pruebas

- Kali Linux
- Web for Pentesters (PentesterLab)

---

## Autor

D1n0