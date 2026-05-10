import requests
from config import CRTSH_TIMEOUT

CRTSH_URL = "https://crt.sh/"

def get_subdomains(domain: str) -> list[str]:
    """
    Dado un dominio, devuelve lista de FQDNs encontrados en CT logs.
    """
    try:
        r = requests.get(
            CRTSH_URL,
            params={"q": f"%.{domain}", "output": "json"},
            timeout=CRTSH_TIMEOUT
        )
        r.raise_for_status()
        entries = r.json()
        subdomains = set()
        for entry in entries:
            name = entry.get("name_value", "")
            for line in name.splitlines():
                line = line.strip().lower()
                if line.endswith(f".{domain}") or line == domain:
                    if "*" not in line:
                        subdomains.add(line)
        return sorted(subdomains)
    except Exception as e:
        print(f"[crtsh] Error al consultar {domain}: {e}")
        return []
