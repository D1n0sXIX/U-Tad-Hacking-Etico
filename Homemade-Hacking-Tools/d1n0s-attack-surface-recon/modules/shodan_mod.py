import shodan
from config import SHODAN_API_KEY

def _get_api():
    if SHODAN_API_KEY == "YOUR_SHODAN_API_KEY":
        return None
    return shodan.Shodan(SHODAN_API_KEY)

def enrich_ips(ips: list[str]) -> dict[str, dict]:
    """
    Dado un listado de IPs activas, consulta Shodan api.host() para cada una.
    Devuelve dict {ip: {"hostnames": [...], "ports": [...], "org": str, "os": str}}
    """
    api = _get_api()
    if not api:
        print("[shodan] API key no configurada, saltando")
        return {}

    results = {}
    for ip in ips:
        try:
            host = api.host(ip)
            results[ip] = {
                "hostnames": host.get("hostnames", []),
                "ports":     [str(s["port"]) for s in host.get("data", [])],
                "org":       host.get("org", ""),
                "os":        host.get("os", "") or "",
            }
            print(f"  [shodan] {ip} → {results[ip]['ports']} | {results[ip]['hostnames']}")
        except shodan.APIError as e:
            if "No information available" not in str(e):
                print(f"  [shodan] Error {ip}: {e}")
        except Exception as e:
            print(f"  [shodan] Error inesperado {ip}: {e}")

    return results
