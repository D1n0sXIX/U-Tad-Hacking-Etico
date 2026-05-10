# ─── Empresas objetivo ───────────────────────────────────────────────────────
# Rellenar con los datos obtenidos en la investigación corporativa previa:
#   - Wikipedia, web corporativa, CNMV, Banco de España, Registro Mercantil
COMPANY_NAMES = [
    {"name": "Nombre actual de la empresa",  "source": "Web corporativa"},
    {"name": "Nombre histórico (si existe)", "source": "Wikipedia"},
    # añadir una entrada por cada filial activa o nombre histórico relevante
]

# ─── ASNs ─────────────────────────────────────────────────────────────────────
# Obtener en https://bgp.he.net → buscar nombre empresa → filtrar Type = ASN
KNOWN_ASNS = ["AS00000"]

# ─── Dominios seed ────────────────────────────────────────────────────────────
# Obtener en https://viewdns.info/reversewhois/ → buscar nombre empresa
# Filtrar: quedarse solo con los que tienen infraestructura real probable
SEED_DOMAINS = [
    "empresa.com",
    "empresa.es",
    # añadir más dominios...
]

# ─── API Keys ─────────────────────────────────────────────────────────────────
# ViewDNS: key gratuita en https://viewdns.info/api/
VIEWDNS_API_KEY = "YOUR_VIEWDNS_API_KEY"

# Shodan: key gratuita en https://account.shodan.io
# Nota: el tier gratuito solo soporta api.host() — no búsqueda por filtros
SHODAN_API_KEY = "YOUR_SHODAN_API_KEY"

# ─── Rutas ────────────────────────────────────────────────────────────────────
TEMPLATE_PATH = "Attack_Surface.xlsx"
OUTPUT_PATH   = "output/Attack_Surface_output.xlsx"

# ─── Timeouts ─────────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 30
CRTSH_TIMEOUT   = 60
