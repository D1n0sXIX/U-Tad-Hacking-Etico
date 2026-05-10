import dns.resolver

def resolve(fqdn: str) -> str:
    """
    Resuelve un FQDN a su dirección IP.
    Devuelve la IP o cadena vacía si no resuelve.
    """
    try:
        answers = dns.resolver.resolve(fqdn, "A")
        return str(answers[0])
    except Exception:
        try:
            answers = dns.resolver.resolve(fqdn, "AAAA")
            return str(answers[0])
        except Exception:
            return ""

def resolve_all(fqdns: list[str]) -> dict[str, str]:
    """
    Resuelve una lista de FQDNs.
    Devuelve dict {fqdn: ip} — ip vacía si no resuelve.
    """
    return {fqdn: resolve(fqdn) for fqdn in fqdns}
