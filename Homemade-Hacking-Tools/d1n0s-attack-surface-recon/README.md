# d1n0s-attack-surface-recon

Herramienta de reconocimiento pasivo de superficie de ataque desarrollada para el módulo de Red Teaming de Hacking Ético (INSO3A) en U-TAD.

Automatiza el proceso de relleno del Excel de Attack Surface Mapping siguiendo la metodología del curso, desde la obtención de ASNs y rangos de red hasta la enumeración y resolución de subdominios.

---

## Requisitos previos

Antes de ejecutar el script es obligatorio realizar la fase de investigación corporativa manual:

1. Buscar nombres históricos y filiales de la empresa objetivo en Wikipedia, web corporativa, CNMV y Banco de España
2. Buscar ASNs en [bgp.he.net](https://bgp.he.net) — filtrar resultados por `Type = ASN`
3. Buscar dominios registrados a nombre de la empresa en [viewdns.info/reversewhois](https://viewdns.info/reversewhois/) — filtrar los que tienen infraestructura real

Con esa información se configura el archivo `config.py` antes de ejecutar.

---

## Instalación

### Dependencias Python

```bash
pip3 install -r requirements.txt --break-system-packages
```

### Herramientas CLI

```bash
# Kali repos
apt-get install amass nmap eyewitness nuclei -y

# Assetfinder
apt-get install assetfinder -y
# Si no está en repos:
go install github.com/tomnomnom/assetfinder@latest
export PATH=$PATH:~/go/bin

# Cloud Enum
git clone https://github.com/initstring/cloud_enum /opt/cloud_enum
pip3 install -r /opt/cloud_enum/requirements.txt --break-system-packages
```

---

## Configuración

Editar `config.py` con los datos obtenidos en la investigación previa:

```python
COMPANY_NAMES = [
    {"name": "Nombre actual de la empresa",  "source": "Web corporativa"},
    {"name": "Nombre histórico",             "source": "Wikipedia"},
    # añadir filiales activas...
]

KNOWN_ASNS = ["AS16203"]   # ASNs encontrados en bgp.he.net

SEED_DOMAINS = [           # Dominios filtrados de ViewDNS Reverse Whois
    "empresa.com",
    "empresa.es",
    # ...
]

VIEWDNS_API_KEY = "tu_api_key"   # https://viewdns.info/api/
SHODAN_API_KEY  = "tu_api_key"   # https://account.shodan.io
```

> Las API keys de ViewDNS y Shodan son gratuitas con registro. Sin ellas, los módulos correspondientes se saltan automáticamente.

---

## Uso

```bash
cd attack_surface_recon/
python3 main.py
```

El resultado se genera en `output/Attack_Surface_<empresa>.xlsx`.

---

## Fases de ejecución

| Fase | Descripción | Fuente |
|------|-------------|--------|
| 1 | ASNs y rangos de red | RIPE Stat API / BGP Tools |
| 2 | Construcción hoja Empresas | config.py + RIPE |
| 3 | Carga de dominios seed | config.py |
| 4 | Reverse NS y Reverse MX | ViewDNS API + dnspython |
| 5 | Dominios adicionales | Amass Intel |
| 6 | Subdominios vía CT logs | crt.sh |
| 7 | Subdominios pasivos | Assetfinder |
| 8 | Subdominios activos | Amass Enum |
| 9 | Resolución DNS | dnspython |
| 10 | Hosts activos en rangos | Nmap ping sweep |
| 11 | Enriquecimiento de IPs | Shodan api.host() |
| 12 | Recursos en nube | Cloud Enum |
| 13 | Generación del Excel | openpyxl |

Tiempo estimado: **30-60 minutos** dependiendo del tamaño de la infraestructura y disponibilidad de Amass.

---

## Estructura del proyecto

```
attack_surface_recon/
├── main.py                  # Orquestador principal
├── config.py                # Configuración del target
├── requirements.txt
├── Attack_Surface.xlsx      # Template Excel (no modificar)
├── modules/
│   ├── bgp.py               # RIPE Stat API — CIDRs por ASN
│   ├── ripe.py              # Confirmación de RIR
│   ├── crtsh.py             # Subdominios via Certificate Transparency
│   ├── viewdns.py           # Reverse NS y Reverse MX
│   ├── amass.py             # Amass intel + enum (subprocess)
│   ├── assetfinder.py       # Assetfinder (subprocess)
│   ├── nmap_scan.py         # Nmap ping sweep (subprocess)
│   ├── dns_resolver.py      # Resolución DNS de FQDNs
│   ├── shodan_mod.py        # Shodan api.host() — enrich IPs
│   └── cloud_enum_mod.py    # Cloud Enum (subprocess)
└── output/
    └── excel_writer.py      # Generación del Excel final
```

---

## Hojas del Excel generado

| Hoja | Columnas automatizadas | Columnas manuales |
|------|----------------------|-------------------|
| Empresas | Nombre, Fuente, RIRs, BGP HE | WhoisXMLAPI Rev. Netblock, WhoisXMLAPI Rev. Whois, Cloud_enum |
| Rangos de red | CIDR, Fuente, ASN, Nmap | Amass |
| Dominios | Fuente, ViewDNS Rev. NS, ViewDNS Rev. MX, Amass Intel, Amass Enum, Assetfinder | Shodan SSL, Subscan, SecurityTrails, Check leaks |
| Subdominios | FQDN, Dominio Padre, Dirección IP, Resolución, Shodan Puertos, Shodan Org | EyeWitness, Nuclei |

---

## Limitaciones conocidas

- **Amass Enum** puede ser terminado por el sistema operativo en máquinas con poca RAM. En ese caso los subdominios quedan cubiertos por crt.sh y Assetfinder.
- **Shodan free tier** solo soporta `api.host()` — no permite búsqueda por filtros como `ssl:`. La columna `Shodan - SSL` de la hoja Dominios debe rellenarse manualmente.
- **RIPE Stat API** puede devolver 403 en algunos entornos. En ese caso el RIR se asume como RIPE para ASNs europeos.
- **ViewDNS Reverse NS/MX** requiere API key. Sin ella, las columnas correspondientes quedan vacías.
- **crt.sh** es inestable bajo carga — el timeout está configurado a 60 segundos por dominio.

---

## Contexto académico

Desarrollado como parte del ejercicio de reconocimiento de activos del módulo de Red Teaming — Hacking Ético, 3º INSO, U-TAD, curso 2025/26.

El uso de esta herramienta está limitado a entornos de prácticas académicas y empresas sobre las que se tenga autorización explícita. El reconocimiento realizado es exclusivamente pasivo — no se realiza ningún tipo de escaneo activo salvo el ping sweep de Nmap sobre los rangos propios identificados.
