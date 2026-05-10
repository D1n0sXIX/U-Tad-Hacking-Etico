import requests
import dns.resolver
from config import VIEWDNS_API_KEY, REQUEST_TIMEOUT

VIEWDNS_BASE = "https://api.viewdns.info"

def _get_ns_records(domain: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(domain, "NS")
        return [str(r.target).rstrip(".") for r in answers]
    except Exception:
        return []

def _get_mx_records(domain: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return [str(r.exchange).rstrip(".") for r in answers]
    except Exception:
        return []

def _reverse_ns(ns: str) -> list[str]:
    if VIEWDNS_API_KEY == "YOUR_VIEWDNS_API_KEY":
        return []
    try:
        r = requests.get(
            f"{VIEWDNS_BASE}/reversens/",
            params={"ns": ns, "apikey": VIEWDNS_API_KEY, "output": "json"},
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        domains = data.get("response", {}).get("domains", [])
        return [d.get("name", "") for d in domains if d.get("name")]
    except Exception as e:
        print(f"[viewdns] Error Reverse NS {ns}: {e}")
        return []

def _reverse_mx(mx: str) -> list[str]:
    if VIEWDNS_API_KEY == "YOUR_VIEWDNS_API_KEY":
        return []
    try:
        r = requests.get(
            f"{VIEWDNS_BASE}/reversemx/",
            params={"mx": mx, "apikey": VIEWDNS_API_KEY, "output": "json"},
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()
        domains = data.get("response", {}).get("domains", [])
        return [d.get("name", "") for d in domains if d.get("name")]
    except Exception as e:
        print(f"[viewdns] Error Reverse MX {mx}: {e}")
        return []

def get_reverse_ns(domain: str) -> dict:
    """
    Devuelve dict con los NS del dominio y los dominios que comparten esos NS.
    {"ns_records": [...], "domains_found": [...]}
    """
    ns_records = _get_ns_records(domain)
    domains_found = set()
    for ns in ns_records:
        domains_found.update(_reverse_ns(ns))
    return {
        "ns_records":    ns_records,
        "domains_found": sorted(domains_found)
    }

def get_reverse_mx(domain: str) -> dict:
    """
    Devuelve dict con los MX del dominio y los dominios que comparten esos MX.
    {"mx_records": [...], "domains_found": [...]}
    """
    mx_records = _get_mx_records(domain)
    domains_found = set()
    for mx in mx_records:
        domains_found.update(_reverse_mx(mx))
    return {
        "mx_records":    mx_records,
        "domains_found": sorted(domains_found)
    }
