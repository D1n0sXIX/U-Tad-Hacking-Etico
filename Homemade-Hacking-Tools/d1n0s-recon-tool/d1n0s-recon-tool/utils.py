import random
import socket
import dns.resolver
import dns.reversename
import requests
import main


#  User-agents
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",

    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

# User-agent rotatorio
def _random_ua():
    return random.choice(_USER_AGENTS)


# HTTP helper - GET con user-agent rotatorio --> devuelve el objeto Response o none
def get(url, params=None, headers=None, timeout=None):
    _headers = {"User-Agent": _random_ua()}
    if headers:
        _headers.update(headers)

    try:
        resp = requests.get(
            url,
            params=params,
            headers=_headers,
            timeout=timeout or main.HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        print(f"[!] HTTP error ({url}): {e}")
        return None


# resolve() --> resuelve hostname a IPs
def resolve(hostname, timeout=None):
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout or main.DNS_TIMEOUT

    try:
        answers = resolver.resolve(hostname, "A")
        return [r.address for r in answers]
    except Exception:
        return []

# ptr() --> consulta PTR inversa de una IP
def ptr(ip, timeout=None):
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout or main.DNS_TIMEOUT

    try:
        rev = dns.reversename.from_address(ip)
        answers = resolver.resolve(rev, "PTR")
        return str(answers[0]).rstrip(".")
    except Exception:
        return None