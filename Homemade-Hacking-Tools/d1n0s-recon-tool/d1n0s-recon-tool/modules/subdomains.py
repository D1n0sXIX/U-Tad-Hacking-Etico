import utils
from output.console import info, warning, print_table


def get_subdomains_info(results):
    target = results["target"]
    info(f"Searching subdomains for: {target}")

    data = []

    for domain in results.get("domains", []):
        data += _from_crtsh(domain["domain"])
        data += _from_hackertarget(domain["domain"])

    results["subdomains"] = _deduplicate(data)
    print_table(
        "Subdomains found",
        ["FQDN", "Parent", "IP", "Resolves"],
        [(s["fqdn"], s["parent"], s["ip"], s["resolves"]) for s in results["subdomains"]]
    )

    return results


def _deduplicate(data):
    seen = set()
    unique = []
    for item in data:
        fqdn = item.get("fqdn", "").lower()
        if fqdn and fqdn not in seen:
            seen.add(fqdn)
            unique.append(item)
    return unique


def _from_crtsh(domain):
    resp = utils.get(
        "https://crt.sh/",
        params={"q": f"%.{domain}", "output": "json"}
    )
    if not resp:
        warning(f"crt.sh no respondió para {domain}")
        return []

    results_list = []
    seen = set()
    for item in resp.json():
        name = item.get("name_value", "")
        for fqdn in name.split("\n"):
            fqdn = fqdn.strip().lstrip("*.")
            if fqdn and fqdn.endswith(domain) and fqdn not in seen:
                seen.add(fqdn)
                ips = utils.resolve(fqdn)
                results_list.append({
                    "fqdn":      fqdn,
                    "parent":    domain,
                    "ip":        ips[0] if ips else "",
                    "resolves":  "Yes" if ips else "No",
                    "eyewitness": "",
                    "nuclei":    "",
                })
    return results_list


def _from_hackertarget(domain):
    resp = utils.get(
        "https://api.hackertarget.com/hostsearch/",
        params={"q": domain}
    )
    if not resp:
        warning(f"HackerTarget no respondió para {domain}")
        return []

    results_list = []
    seen = set()
    for line in resp.text.splitlines():
        parts = line.split(",")
        if len(parts) >= 2:
            fqdn = parts[0].strip()
            ip   = parts[1].strip()
            if fqdn and fqdn.endswith(domain) and fqdn not in seen:
                seen.add(fqdn)
                results_list.append({
                    "fqdn":      fqdn,
                    "parent":    domain,
                    "ip":        ip,
                    "resolves":  "Yes" if ip else "No",
                    "eyewitness": "",
                    "nuclei":    "",
                })
    return results_list