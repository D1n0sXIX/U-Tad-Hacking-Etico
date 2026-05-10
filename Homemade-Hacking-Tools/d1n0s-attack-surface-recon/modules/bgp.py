import requests
from config import REQUEST_TIMEOUT

RIPE_PREFIXES_URL = "https://stat.ripe.net/data/announced-prefixes/data.json"

def get_prefixes(asn: str) -> list[dict]:
    """
    Dado un ASN (ej: 'AS16203'), devuelve lista de dicts:
    {"cidr": "213.170.41.0/24", "asn": "AS16203", "fuente": "RIPE Stat"}
    """
    asn_clean = asn.upper().replace("AS", "")
    try:
        r = requests.get(
            RIPE_PREFIXES_URL,
            params={"resource": f"AS{asn_clean}"},
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        prefixes = data.get("data", {}).get("prefixes", [])
        return [
            {
                "cidr":   p["prefix"],
                "asn":    f"AS{asn_clean}",
                "fuente": "RIPE Stat / BGP HE"
            }
            for p in prefixes
            if ":" not in p["prefix"]  # Filtra IPv6
        ]
    except Exception as e:
        print(f"[bgp] Error al consultar AS{asn_clean}: {e}")
        return []
