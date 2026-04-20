import utils
from ipwhois import IPWhois
from output.console import info, success, warning
from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(resp.text, "html.parser")
    # print para depuración, muestra los primeros 5000 caracteres del HTML
    # print(resp.text[:5000])
    for row in soup.select("div#search table tbody tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            asn  = cols[0].get_text(strip=True)
            name = cols[2].get_text(strip=True).encode('latin-1').decode('utf-8')
            flag = cols[2].find("img")
            country = flag["title"] if flag else ""

            if asn.startswith("AS"):
                results_list.append({
                    "asn":     asn,
                    "name":    name,
                    "country": country,
                    "cidr":    "",
                    "source":  "bgphe",
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

    results["asns"]   = _deduplicate_asns(data)
    results["ranges"] = _extract_ranges(data)

    return results