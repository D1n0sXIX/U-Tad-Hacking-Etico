# Tema 1 — Hacking de Aplicaciones Web

Prácticas de **SQL Injection**, **XSS**, **XXE**, **File Upload** y **pivoting con reGeorg**.  
Asignatura: Hacking Ético | U-TAD 2025-2026 | D1n0

---

## Estructura

| Carpeta | Contenido |
|---|---|
| [`SQLi/`](./SQLi/) | Inyección SQL manual y con SQLMap — UNION, Blind, Time-based, escalada a RCE |
| [`XSS/`](./XSS/) | Cross-Site Scripting — tipos, payloads, evasión de filtros, BeEF |
| [`XXE/`](./XXE/) | XML External Entity — lectura de ficheros, Blind XXE, SSRF, RCE |
| [`FileUpload/`](./FileUpload/) | Evasión de filtros en subida de ficheros — blacklist, whitelist, magic bytes |
| [`reGeorg/`](./reGeorg/) | HTTP tunneling y pivoting a redes internas via webshell PHP |

---

## Metodología general (6 fases)

1. **Obtención de información** — reconocimiento pasivo y activo
2. **Enumeración** — puertos, servicios, tecnologías
3. **Análisis** — identificar vectores de ataque
4. **Explotación** — ejecución del ataque
5. **Post-explotación** — escalada, persistencia, pivoting
6. **Documentación** — informe de auditoría

---

## Plataformas de prácticas

- [DVWA](http://www.dvwa.co.uk/) — Damn Vulnerable Web Application
- [PentesterLab — Web for Pentesters](https://pentesterlab.com/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

---
