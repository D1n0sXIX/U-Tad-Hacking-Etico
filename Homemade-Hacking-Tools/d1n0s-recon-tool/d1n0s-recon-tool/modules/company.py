import utils
from output.console import info, success, warning

# Fuentes
def _from_wikipedia(target):
    # Busqueda en Wikipedia por el nombre
    resp = utils.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": target,
            "format": "json"
        }
    )
    if not resp:
        warning("Wikipedia API no respondió")
        return []

    # Guardar resultados en json
    data = resp.json()

    if not data["query"]["search"]:
        return []

    results_list = []
    for item in data["query"]["search"]:
        results_list.append({
            "name": item["title"],
            "source": "wikipedia",
            "subsidiaries": [],
            "former_names": [],
            "providers": [],
            "countries": [],
        })

    
    return results_list
# Otras fuentes:
def _from_wikidata(target):
    resp = utils.get(
        "https://www.wikidata.org/w/api.php",
        params={
            "action": "wbsearchentities",
            "search": target,
            "language": "en",
            "format": "json"
        }
    )
    if not resp:
        warning("Wikidata API no respondió")
        return []

    data = resp.json()

    if not data["search"]:
        return []

    results_list = []
    for item in data["search"]:
        results_list.append({
            "name": item["label"],
            "source": "wikidata",
            "subsidiaries": [],
            "former_names": [],
            "providers": [],
            "countries": [],
        })
    return results_list

def _from_duckduckgo(target):
    resp = utils.get(
        "https://api.duckduckgo.com/",
        params={
            "q": target,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
    )
    if not resp:
        warning("DuckDuckGo API no respondió")
        return []

    data = resp.json()

    if not data.get("RelatedTopics"):
        return []

    results_list = []
    for item in data["RelatedTopics"]:
        if "Text" in item:
            results_list.append({
                "name": item["Text"].split(" - ")[0],
                "source": "duckduckgo",
                "subsidiaries": [],
                "former_names": [],
                "providers": [],
                "countries": [],
            })
    return results_list

def _deduplicate(data):
    seen = set()
    unique = []
    for item in data:
        name = item.get("name", "").lower()
        if name and name not in seen:
            seen.add(name)
            unique.append(item)
    return unique

def get_company_info(results):
    target = results["target"]
    info(f"Searching company info for: {target}")

    data = []

    # Fuentes
    data += _from_wikipedia(target)
    data += _from_wikidata(target)
    data += _from_duckduckgo(target)

    # Limpiar duplicados y agregar
    results["companies"] = _deduplicate(data)

    return results