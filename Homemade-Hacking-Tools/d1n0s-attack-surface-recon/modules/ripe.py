import requests
from config import REQUEST_TIMEOUT

RIPE_OVERVIEW_URL = "https://stat.ripe.net/data/as-overview/data.json"

def get_rir(asn: str) -> str:
    """
    Dado un ASN, devuelve el RIR correspondiente (ej: 'RIPE').
    """
    asn_clean = asn.upper().replace("AS", "")
    try:
        r = requests.get(
            RIPE_OVERVIEW_URL,
            params={"resource": f"AS{asn_clean}"},
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        rir = data.get("data", {}).get("rir", "")
        return rir if rir else "RIPE"
    except Exception as e:
        print(f"[ripe] Error al consultar AS{asn_clean}: {e}")
        return "RIPE"
