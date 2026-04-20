import utils
import ipaddress
from output.console import info, warning, print_table

def _from_crtsh(target):
    resp = utils.get(
        "https://crt.sh/",
        params={"q": target, "output": "json"}
    )
    if not resp:
        warning("crt.sh no respondió")
        return []

    results_list = []
    seen = set()
    for item in resp.json():
        name = item.get("name_value", "")
        for domain in name.split("\n"):
            domain = domain.strip().lstrip("*.")
            if domain and "." in domain and domain not in seen:
                seen.add(domain)
                results_list.append({
                    "domain": domain,
                    "source": "crtsh",
                })
    return results_list


def _from_ripe(asn):
    resp = utils.get(
        "https://stat.ripe.net/data/announced-prefixes/data.json",
        params={"resource": asn}
    )
    if not resp:
        warning(f"RIPE no respondió para {asn}")
        return []

    data = resp.json()
    prefixes = data.get("data", {}).get("prefixes", [])

    results_list = []
    for prefix in prefixes:
        cidr_text = prefix.get("prefix", "")
        try:
            network = ipaddress.ip_network(cidr_text, strict=False)
            first_ip = str(next(network.hosts()))
            hostname = utils.ptr(first_ip)
            if hostname:
                parts = hostname.split(".")
                domain = ".".join(parts[-2:]) if len(parts) >= 2 else hostname
                results_list.append({
                    "domain": domain,
                    "source": "ripe_ptr",
                })
        except Exception:
            continue

    return results_list

def _from_hackertarget(target):
    resp = utils.get(
        "https://api.hackertarget.com/hostsearch/",
        params={"q": target}
    )
    if not resp:
        warning("HackerTarget no respondió")
        return []

    results_list = []
    seen = set()
    for line in resp.text.splitlines():
        parts = line.split(",")
        if len(parts) >= 1:
            domain = parts[0].strip()
            if domain and "." in domain and domain not in seen:
                seen.add(domain)
                results_list.append({
                    "domain": domain,
                    "source": "hackertarget",
                })
    return results_list

def _deduplicate(data):
    seen = set()
    unique = []
    for item in data:
        domain = item.get("domain", "").lower()
        if domain and domain not in seen:
            seen.add(domain)
            unique.append(item)
    return unique


def get_domains_info(results):
    target = results["target"]
    info(f"Searching domains for: {target}")
    domain_guess = target.lower().replace(" ", "") + ".com"

    data = []
    
    data += _from_crtsh(target)
    data += _from_hackertarget(domain_guess)

    for asn in results.get("asns", []):
        data += _from_ripe(asn["asn"])

    results["domains"] = _deduplicate(data)
    print_table(
        "Domains found",
        ["Domain", "Source"],
        [(d["domain"], d["source"]) for d in results["domains"]]
    )

    return results
