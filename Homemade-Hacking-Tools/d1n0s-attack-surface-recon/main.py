#!/usr/bin/env python3
import sys
import shutil
from rich.console import Console
from rich.table   import Table
from rich.progress import track

sys.path.insert(0, ".")

from config import COMPANY_NAMES, KNOWN_ASNS, SEED_DOMAINS
from modules import bgp, ripe, crtsh, viewdns, amass, assetfinder, nmap_scan, dns_resolver, cloud_enum_mod, shodan_mod
from output  import excel_writer

console = Console()

def banner():
    console.print("""
[bold cyan]╔══════════════════════════════════════════╗
║      Attack Surface Recon Tool           ║
║      ABANCA - Ethical Hacking INSO3A     ║
╚══════════════════════════════════════════╝[/bold cyan]
""")

def check_tools():
    tools = {
        "amass":       shutil.which("amass"),
        "assetfinder": shutil.which("assetfinder"),
        "nmap":        shutil.which("nmap"),
    }
    t = Table(title="Estado de herramientas")
    t.add_column("Herramienta")
    t.add_column("Estado")
    for name, path in tools.items():
        status = f"[green]OK  {path}[/green]" if path else "[red]No instalada[/red]"
        t.add_row(name, status)
    console.print(t)

def run():
    banner()
    check_tools()

    data = {
        "empresas":    [],
        "rangos":      [],
        "dominios":    {},   # dominio → dict de flags
        "subdominios": {},   # fqdn → dict
    }

    # ─── 1. BGP + RIPE por cada ASN ──────────────────────────────────────────
    console.rule("[bold]Fase 1 · ASNs y Rangos de red[/bold]")
    rir_map = {}
    for asn in KNOWN_ASNS:
        console.print(f"[cyan]→ RIPE Stat: {asn}[/cyan]")
        rir = ripe.get_rir(asn)
        rir_map[asn] = rir
        prefixes = bgp.get_prefixes(asn)
        for p in prefixes:
            data["rangos"].append({
                "cidr":         p["cidr"],
                "fuente":       p["fuente"],
                "asn":          p["asn"],
                "nmap_activos": []
            })
            console.print(f"  [green]+[/green] {p['cidr']}")

    # ─── 2. Tabla de empresas ────────────────────────────────────────────────
    console.rule("[bold]Fase 2 · Empresas[/bold]")
    ASN_CONFIRMED = {"ABANCA CORPORACIÓN BANCARIA", "NCG BANCO"}
    for company in COMPANY_NAMES:
        name_upper = company["name"].upper()
        tiene_asn = any(kw in name_upper for kw in ASN_CONFIRMED)
        bgp_he = ", ".join(KNOWN_ASNS) if tiene_asn else ""
        rir    = list(rir_map.values())[0] if tiene_asn else ""
        data["empresas"].append({
            "nombre":     company["name"],
            "fuente":     company["source"],
            "rir":        rir,
            "bgp_he":     bgp_he,
            "cloud_enum": "Manual"
        })
        console.print(f"  + {company['name']}")

    # ─── 3. Inicializar dominios con seed ────────────────────────────────────
    console.rule("[bold]Fase 3 · Dominios seed[/bold]")
    for domain in SEED_DOMAINS:
        data["dominios"][domain] = {
            "dominio":     domain,
            "fuente":      "ViewDNS Reverse Whois",
            "amass_intel": False,
            "rev_ns":      "",
            "rev_mx":      "",
            "amass_enum":  False,
            "assetfinder": False,
        }
        console.print(f"  [green]+[/green] {domain}")

    # ─── 4. ViewDNS Reverse NS y MX ─────────────────────────────────────────
    console.rule("[bold]Fase 4 · ViewDNS Reverse NS / MX[/bold]")
    main_domains = ["abanca.com", "abanca.es", "abanca.pt"]
    for domain in main_domains:
        console.print(f"[cyan]→ ViewDNS NS/MX: {domain}[/cyan]")
        ns_data = viewdns.get_reverse_ns(domain)
        mx_data = viewdns.get_reverse_mx(domain)

        ns_str = ", ".join(ns_data["ns_records"])
        mx_str = ", ".join(mx_data["mx_records"])

        if domain in data["dominios"]:
            data["dominios"][domain]["rev_ns"] = ns_str
            data["dominios"][domain]["rev_mx"] = mx_str

        for d in ns_data["domains_found"] + mx_data["domains_found"]:
            if d not in data["dominios"]:
                data["dominios"][d] = {
                    "dominio":     d,
                    "fuente":      "ViewDNS Reverse NS/MX",
                    "amass_intel": False,
                    "rev_ns":      ns_str if d in ns_data["domains_found"] else "",
                    "rev_mx":      mx_str if d in mx_data["domains_found"] else "",
                    "amass_enum":  False,
                    "assetfinder": False,
                }
                console.print(f"  [green]+[/green] {d} (via ViewDNS)")

    # ─── 5. Amass Intel ──────────────────────────────────────────────────────
    console.rule("[bold]Fase 5 · Amass Intel[/bold]")
    amass_intel_domains = amass.intel("ABANCA", "abanca.com")
    for d in amass_intel_domains:
        if d not in data["dominios"]:
            data["dominios"][d] = {
                "dominio":     d,
                "fuente":      "Amass Intel",
                "amass_intel": True,
                "rev_ns":      "",
                "rev_mx":      "",
                "amass_enum":  False,
                "assetfinder": False,
            }
        else:
            data["dominios"][d]["amass_intel"] = True
        console.print(f"  [green]+[/green] {d} (Amass Intel)")

    # ─── 6. Subdominios: crt.sh ──────────────────────────────────────────────
    console.rule("[bold]Fase 6 · Subdominios via crt.sh[/bold]")
    for domain in track(list(data["dominios"].keys()), description="crt.sh..."):
        subs = crtsh.get_subdomains(domain)
        for fqdn in subs:
            if fqdn not in data["subdominios"]:
                data["subdominios"][fqdn] = {
                    "fqdn":         fqdn,
                    "dominio_padre": domain,
                    "ip":           "",
                    "amass_enum":   False,
                    "assetfinder":  False,
                    "crtsh":        True,
                }

    console.print(f"  [green]+[/green] {len(data['subdominios'])} subdominios encontrados (crt.sh)")

    # ─── 7. Subdominios: Assetfinder ─────────────────────────────────────────
    console.rule("[bold]Fase 7 · Assetfinder[/bold]")
    for domain in track(list(data["dominios"].keys())[:5], description="Assetfinder..."):
        subs = assetfinder.find(domain)
        for fqdn in subs:
            if fqdn not in data["subdominios"]:
                data["subdominios"][fqdn] = {
                    "fqdn":         fqdn,
                    "dominio_padre": domain,
                    "ip":           "",
                    "amass_enum":   False,
                    "assetfinder":  True,
                    "crtsh":        False,
                }
            else:
                data["subdominios"][fqdn]["assetfinder"] = True
        if subs:
            data["dominios"][domain]["assetfinder"] = True

    # ─── 8. Subdominios: Amass Enum ───────────────────────────────────────────
    console.rule("[bold]Fase 8 · Amass Enum[/bold]")
    for domain in ["abanca.com", "abanca.es"]:
        subs = amass.enum(domain)
        for fqdn in subs:
            if fqdn not in data["subdominios"]:
                data["subdominios"][fqdn] = {
                    "fqdn":         fqdn,
                    "dominio_padre": domain,
                    "ip":           "",
                    "amass_enum":   True,
                    "assetfinder":  False,
                    "crtsh":        False,
                }
            else:
                data["subdominios"][fqdn]["amass_enum"] = True
        if subs:
            data["dominios"][domain]["amass_enum"] = True

    # ─── 9. DNS Resolution ───────────────────────────────────────────────────
    console.rule("[bold]Fase 9 · Resolución DNS[/bold]")
    fqdns = list(data["subdominios"].keys())
    resolved = dns_resolver.resolve_all(fqdns)
    activos = 0
    for fqdn, ip in resolved.items():
        data["subdominios"][fqdn]["ip"] = ip
        if ip:
            activos += 1
    console.print(f"  {activos}/{len(fqdns)} subdominios resuelven")

    # ─── 10. Nmap sobre rangos ────────────────────────────────────────────────
    console.rule("[bold]Fase 10 · Nmap ping sweep[/bold]")
    for rango in data["rangos"]:
        console.print(f"[cyan]→ Nmap: {rango['cidr']}[/cyan]")
        activos = nmap_scan.ping_sweep(rango["cidr"])
        rango["nmap_activos"] = activos
        console.print(f"  [green]+[/green] {len(activos)} hosts activos")

    # ─── 11. Shodan enrich ───────────────────────────────────────────────────
    console.rule("[bold]Fase 11 · Shodan enrich (api.host)[/bold]")
    all_active_ips = []
    for rango in data["rangos"]:
        all_active_ips.extend(rango.get("nmap_activos", []))
    for s in data["subdominios"].values():
        if s.get("ip") and s["ip"] not in all_active_ips:
            all_active_ips.append(s["ip"])

    shodan_data = shodan_mod.enrich_ips(list(set(all_active_ips)))
    data["shodan"] = shodan_data

    for s in data["subdominios"].values():
        ip = s.get("ip", "")
        if ip and ip in shodan_data:
            s["shodan_ports"] = ", ".join(shodan_data[ip]["ports"])
            s["shodan_org"]   = shodan_data[ip]["org"]
        else:
            s["shodan_ports"] = ""
            s["shodan_org"]   = ""

    # ─── 12. Cloud Enum ──────────────────────────────────────────────────────
    console.rule("[bold]Fase 12 · Cloud Enum[/bold]")
    cloud_results = cloud_enum_mod.scan(["abanca", "ncgbanco", "novacaixagalicia"])
    cloud_str = "\n".join(cloud_results) if cloud_results else "Sin resultados"
    for e in data["empresas"]:
        if "ABANCA Corporación" in e["nombre"]:
            e["cloud_enum"] = cloud_str

    # ─── 13. Escribir Excel ───────────────────────────────────────────────────
    console.rule("[bold]Fase 13 · Generando Excel[/bold]")
    final_data = {
        "empresas":   data["empresas"],
        "rangos":     data["rangos"],
        "dominios":   list(data["dominios"].values()),
        "subdominios": list(data["subdominios"].values()),
    }
    excel_writer.write(final_data)

    # ─── Resumen ─────────────────────────────────────────────────────────────
    console.rule("[bold green]Resumen[/bold green]")
    t = Table()
    t.add_column("Hoja")
    t.add_column("Registros", justify="right")
    t.add_row("Empresas",    str(len(data["empresas"])))
    t.add_row("Rangos de red", str(len(data["rangos"])))
    t.add_row("Dominios",    str(len(data["dominios"])))
    t.add_row("Subdominios", str(len(data["subdominios"])))
    console.print(t)

if __name__ == "__main__":
    run()
