# d1n0-recon-tool

Herramienta modular de reconocimiento de activos para ejercicios Red Team. Automatiza el proceso completo de identificación de superficie de ataque: desde el análisis de la empresa hasta la enumeración de subdominios y servicios expuestos.

> Desarrollada como parte del módulo de Red Teaming — Hacking Ético, U-TAD 2025/26

---

## Flujo de reconocimiento

```
Empresa → ASN / Rangos de red → Dominios → Subdominios → Enumeración
```

Cada módulo recibe el output del anterior y vuelca los resultados en consola y en el Excel de superficie de ataque.

---

## Estructura del proyecto

```
d1n0-recon-tool/
│
├── main.py                  # Entry point. Argparse, timeouts globales, flujo principal
│
├── modules/
│   ├── company.py           # Análisis de la empresa: filiales, nombres anteriores, proveedores
│   ├── asn.py               # Identificación de ASNs y rangos de red (BGP HE, RIRs, WhoisXMLAPI)
│   ├── domains.py           # Dominios: reverse CIDR, reverse WHOIS, reverse NS/MX
│   ├── subdomains.py        # Subdominios: crt.sh, Amass, Assetfinder, fuerza bruta DNS
│   └── enumerate.py         # Enumeración: Shodan, httpx, Nuclei, EyeWitness
│
├── utils.py                 # HTTP helper (user-agent rotatorio) + DNS helper compartidos
│
└── output/
    ├── excel_writer.py      # Rellena Attack_Surface.xlsx con los resultados
    └── console.py           # Pretty print con rich
```

---

## Módulos

### `modules/company.py`
Punto de partida del reconocimiento. Dado el nombre de una organización, busca:
- Nombres anteriores y variantes en otros países
- Filiales y empresas subsidiarias
- Proveedores relevantes

Fuentes: búsqueda web, Wikipedia, web oficial.

### `modules/asn.py`
Identifica los sistemas autónomos y rangos de red registrados a nombre de la organización.

| Fuente | Método |
|---|---|
| BGP Hurricane | `http://bgp.he.net/` — ASNs + rangos CIDR |
| RIRs (ARIN, RIPE…) | Consulta WHOIS por nombre de org |
| WhoisXMLAPI | Reverse Netblocks — rangos sin ASN propio |
| Amass | `amass intel -org <org>` |

### `modules/domains.py`
Identifica dominios principales a partir de los rangos de red encontrados.

| Técnica | Herramienta |
|---|---|
| Reverse CIDR / PTR | IPIP, WhoisXMLAPI, bgp.tools |
| Reverse WHOIS | WhoisXMLAPI |
| Reverse NS | viewdns.info/reversens |
| Reverse MX | viewdns.info/reversemx |

### `modules/subdomains.py`
Enumeración pasiva y activa de subdominios para cada dominio identificado.

- **Pasivo:** crt.sh, VirusTotal, SecurityTrails, DNSdumpster
- **Herramientas:** Amass (`enum -passive`), Assetfinder
- **Fuerza bruta:** resolución masiva con diccionario (SecLists — `bitquark-subdomains-top100000.txt`)

### `modules/enumerate.py`
Enumeración de la superficie de ataque sobre todos los activos encontrados.

- Escaneo de puertos pasivo via Shodan
- Validación de hosts web activos con httpx
- Captura de screenshots con EyeWitness / GoWitness
- Detección automática de vulnerabilidades con Nuclei

---

## Utilidades

### `utils.py`
Funciones compartidas entre módulos para evitar código duplicado:
- `get(url)` — request HTTP con user-agent rotatorio, timeout global y manejo de errores
- `resolve(hostname)` — resolución DNS de hostname a IP
- `ptr(ip)` — consulta PTR inversa

---

## Output

### `output/excel_writer.py`
Vuelca los resultados en `Attack_Surface.xlsx` siguiendo la estructura de hojas:

| Hoja | Campos |
|---|---|
| Empresas | Nombre, Fuente, RIRs, BGP HE, WhoisXML Netblock, WhoisXML Whois, Cloud_enum |
| Rangos de red | CIDR, Fuente, ASN, Amass, Nmap |
| Dominios | Dominio, Fuente, Amass Intel, Reverse NS, Reverse MX, Amass Enum, Assetfinder, Shodan SSL, Subscan, SecurityTrails, Leaks |
| Subdominios | FQDN, Dominio Padre, IP, Resolución, EyeWitness, Nuclei |

### `output/console.py`
Output por consola usando `rich`. Muestra los resultados por fases con colores y tablas.

---

## APIs requeridas

| Servicio | Key necesaria | Free tier | Uso |
|---|---|---|---|
| Shodan | Sí | Sí (limitado) | Enumeración pasiva de puertos |
| WhoisXMLAPI | Sí | Sí | Reverse Netblocks, Reverse WHOIS |
| BGP Hurricane | No | — | ASNs y rangos |
| crt.sh | No | — | Subdominios por certificados SSL |
| viewdns.info | No | — | Reverse NS / MX |
| ipwhois | No | — | Consultas WHOIS/RIR locales |

Las API keys se configuran como variables de entorno:

```bash
export SHODAN_API_KEY="..."
export WHOISXML_API_KEY="..."
```

---

## Instalación

```bash
git clone https://github.com/D1n0/d1n0-recon-tool
cd d1n0s-recon-tool
pip install -r requirements.txt
```

**Dependencias principales:**
```
requests
dnspython
ipwhois
shodan
openpyxl
rich
```

---

## Uso

```bash
# Reconocimiento completo
python main.py -t "Nombre Empresa"

# Solo un módulo concreto
python main.py -t "Nombre Empresa" --only asn
python main.py -t "Nombre Empresa" --only subdomains

# Módulos disponibles: company, asn, domains, subdomains, enumerate

# Especificar output Excel
python main.py -t "Nombre Empresa" --output Attack_Surface.xlsx
```

---

## Metodología de referencia

Basado en el flujo de reconocimiento del Tema 2 — Técnicas de Red Teaming (U-TAD 25/26):

1. **Análisis de la empresa** — identificar todas las entidades dentro del alcance
2. **Sistemas autónomos** — BGP HE + RIRs → rangos CIDR
3. **Rangos adicionales** — WhoisXMLAPI Reverse Netblocks
4. **Dominios principales** — Reverse CIDR/PTR + Reverse WHOIS + Reverse NS/MX
5. **Subdominios** — enumeración pasiva + fuerza bruta activa
6. **Enumeración** — puertos, apps web, tecnologías, vulnerabilidades

---

*d1n0 · U-TAD Hacking Ético 2025/26*