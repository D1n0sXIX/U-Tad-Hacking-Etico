import utils
from ipwhois import IPWhois
from output.console import info, success, warning

def _extract_ranges(data):
    seen = set()
    ranges = []
    for item in data:
        cidr = item.get("cidr", "")
        if cidr and cidr not in seen:
            seen.add(cidr)
            ranges.append({
                "cidr":   cidr,
                "source": item.get("source", ""),
                "asn":    item.get("asn", ""),
                "amass":  "",
                "nmap":   "",
            })
    return ranges

def _from_bgphe(target):
    resp = utils.get(
        "https://bgp.he.net/search",
        params={"search[search]": target, "commit": "Search"}
    )
    if not resp:
        warning("BGP Hurricane no respondió")
        return []

    results_list = []
    # BGP HE devuelve HTML, hay que parsearlo
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    for row in soup.select("table#search tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            asn  = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            if asn.startswith("AS"):
                results_list.append({
                    "asn":     asn,
                    "name":    name,
                    "cidr":    "",
                    "source":  "bgphe",
                    "country": "",
                })
    return results_list

def _from_whoisxmlapi(target):
    import config
    if not config.WHOISXML_API_KEY:
        warning("WhoisXMLAPI key no configurada")
        return []

    resp = utils.get(
        "https://ip-netblocks.whoisxmlapi.com/api/v2",
        params={
            "apiKey": config.WHOISXML_API_KEY,
            "org":    target,
        }
    )
    if not resp:
        warning("WhoisXMLAPI no respondió")
        return []

    data = resp.json()
    results_list = []
    for item in data.get("inetnums", []):
        results_list.append({
            "asn":     item.get("as", {}).get("asn", ""),
            "name":    item.get("org", ""),
            "cidr":    item.get("inetnum", ""),
            "source":  "whoisxmlapi",
            "country": item.get("country", ""),
        })
    return results_list

def _deduplicate_asns(data):
    seen = set()
    unique = []
    for item in data:
        asn = item.get("asn", "").upper()
        if asn and asn not in seen:
            seen.add(asn)
            unique.append(item)
    return unique

def get_asn_info(results):
    target = results["target"]
    info(f"Searching ASN info for: {target}")

    data = []
    data += _from_bgphe(target)
    data += _from_whoisxmlapi(target)

    results["asns"]   = _deduplicate_asns(data)
    results["ranges"] = _extract_ranges(data)

    return results