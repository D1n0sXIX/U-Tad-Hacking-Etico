#!/usr/bin/env python3
# nmap_reader.py
# D1n0 / Alejandro Mamán López-Mingo - INSO3A - 2024-06
# Partially made with Claude
"""
nmap_reader.py — Nmap output reader (XML and plain text)
Usage: python3 nmap_reader.py <file.xml|file.txt|file.nmap> [...]
       python3 nmap_reader.py *.xml *.txt
"""

import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path

# Optional: Rich for colored/formatted output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None



#  PARSERS


def parse_xml(filepath):
    # Load and parse XML
    tree = ET.parse(filepath)
    root = tree.getroot()

    # General scan info
    scan_info = {
        "args":    root.get("args", "N/A"),
        "start":   root.get("startstr", "N/A"),
        "version": root.get("version", "N/A"),
        "source":  "xml",
    }

    # Scan elapsed time
    runstats = root.find("runstats/finished")
    scan_info["elapsed"] = (runstats.get("elapsed", "?") + "s") if runstats is not None else "N/A"

    # List of hosts
    hosts = []
    for host in root.findall("host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        # Addresses (IPv4, IPv6, MAC...)
        addrs = {}
        for addr in host.findall("address"):
            addrs[addr.get("addrtype")] = addr.get("addr")

        # Hostnames
        hostnames = [hn.get("name") for hn in host.findall("hostnames/hostname")]

        # OS detection matches
        os_matches = [
            {"name": m.get("name"), "accuracy": m.get("accuracy")}
            for m in host.findall("os/osmatch")
        ]

        # Ports
        ports = []
        for port in host.findall("ports/port"):
            state_el = port.find("state")
            svc_el   = port.find("service")
            state    = state_el.get("state") if state_el is not None else "?"

            # NSE scripts output for this port
            scripts = [
                {"id": s.get("id"), "output": s.get("output", "").strip()}
                for s in port.findall("script")
            ]

            # Service name — append tunnel type if present (e.g. ssl)
            service = svc_el.get("name", "") if svc_el is not None else ""
            tunnel  = svc_el.get("tunnel", "") if svc_el is not None else ""
            if tunnel:
                service = f"{service}/{tunnel}"

            ports.append({
                "portid":  port.get("portid"),
                "proto":   port.get("protocol"),
                "state":   state,
                "reason":  state_el.get("reason", "") if state_el is not None else "",
                "service": service,
                "version": " ".join(filter(None, [
                    svc_el.get("product", "")   if svc_el is not None else "",
                    svc_el.get("version", "")   if svc_el is not None else "",
                    svc_el.get("extrainfo", "") if svc_el is not None else "",
                ])).strip(),
                "scripts": scripts,
            })

        uptime_el = host.find("uptime")
        hosts.append({
            "addrs":     addrs,
            "hostnames": hostnames,
            "os":        os_matches,
            "ports":     ports,
            "uptime":    uptime_el.get("lastboot", "") if uptime_el is not None else "",
        })

    return scan_info, hosts


# Regex patterns for plain text parsing (heuristic-based, may not cover all cases)

RE_SCAN_START = re.compile(r"Starting Nmap ([\d.]+).+?at (.+)", re.IGNORECASE)
RE_HOST       = re.compile(r"Nmap scan report for (.+)")
RE_MAC        = re.compile(r"MAC Address:\s*([\w:]+)\s*(?:\((.+)\))?")
RE_PORT       = re.compile(
    r"^(\d+)/(tcp|udp)\s+(open(?:\|filtered)?|closed|filtered)\s+(\S+)?\s*(.*)?$"
)
RE_SCRIPT     = re.compile(r"^\|[_\s]?(.+?):?\s*(.*)")
RE_OS_DETAIL  = re.compile(r"OS details?:\s*(.+)", re.IGNORECASE)
RE_OS_GUESS   = re.compile(r"Aggressive OS guesses?:\s*(.+)", re.IGNORECASE)
RE_ELAPSED    = re.compile(r"Nmap done.+?(\d+[\d.]*)\s*seconds")
RE_IP_EXTRACT = re.compile(r"\(?([\d.]+)\)?$")


def parse_txt(filepath):
    text = Path(filepath).read_text(errors="replace")
    lines = text.splitlines()

    scan_info = {
        "args": "N/A", "start": "N/A", "version": "N/A",
        "elapsed": "N/A", "source": "txt",
    }
    hosts = []
    current_host = None
    current_port = None
    pending_scripts = []

    def flush_port():
        nonlocal current_port
        if current_port is not None:
            current_port["scripts"].extend(pending_scripts)
            pending_scripts.clear()
            current_host["ports"].append(current_port)
            current_port = None

    def flush_host():
        nonlocal current_host
        if current_host is not None:
            flush_port()
            hosts.append(current_host)
            current_host = None

    for raw_line in lines:
        line = raw_line.rstrip()

        # Scan header
        m = RE_SCAN_START.search(line)
        if m:
            scan_info["version"] = m.group(1)
            scan_info["start"]   = m.group(2).strip()
            continue

        m = RE_ELAPSED.search(line)
        if m:
            scan_info["elapsed"] = m.group(1) + "s"
            continue

        # New host block
        m = RE_HOST.match(line)
        if m:
            flush_host()
            raw  = m.group(1).strip()
            ip_m = RE_IP_EXTRACT.search(raw)
            ip   = ip_m.group(1) if ip_m else ""
            hostname = raw.replace(f"({ip})", "").strip() if ip and ip != raw else ""
            current_host = {
                "addrs":     {"ipv4": ip} if ip else {},
                "hostnames": [hostname] if hostname else [],
                "os":        [],
                "ports":     [],
                "uptime":    "",
                "_raw_host": raw,
            }
            current_port = None
            pending_scripts.clear()
            continue

        if current_host is None:
            continue

        # MAC address
        m = RE_MAC.match(line)
        if m:
            current_host["addrs"]["mac"] = m.group(1)
            continue

        # OS detection
        m = RE_OS_DETAIL.search(line) or RE_OS_GUESS.search(line)
        if m:
            for part in m.group(1).split(","):
                acc_m = re.search(r"\((\d+)%\)", part)
                name  = re.sub(r"\(\d+%\)", "", part).strip().strip(",").strip()
                if name:
                    current_host["os"].append({
                        "name":     name,
                        "accuracy": acc_m.group(1) if acc_m else "?",
                    })
            continue

        # Port line
        m = RE_PORT.match(line.strip())
        if m:
            # Flush previous port before starting a new one
            if current_port is not None:
                current_port["scripts"].extend(pending_scripts)
                pending_scripts.clear()
                current_host["ports"].append(current_port)

            portid, proto, state, service, version_raw = (
                m.group(1), m.group(2), m.group(3),
                m.group(4) or "", m.group(5) or "",
            )
            current_port = {
                "portid":  portid,
                "proto":   proto,
                "state":   state.split("|")[0],  # open|filtered → open
                "reason":  "",
                "service": service,
                "version": version_raw.strip(),
                "scripts": [],
            }
            continue

        # NSE script output lines (start with | or |_)
        stripped = line.lstrip()
        if stripped.startswith("|") and current_port is not None:
            m = RE_SCRIPT.match(stripped)
            if m:
                sid = m.group(1).strip().rstrip(":")
                out = m.group(2).strip()
                # Continuation of previous script (no clear ID)
                if pending_scripts and not out and not re.match(r"[\w\-]+", sid):
                    pending_scripts[-1]["output"] += " " + sid
                else:
                    pending_scripts.append({"id": sid, "output": out})

    flush_host()
    return scan_info, hosts


#  DISPLAY

def _state_rich(state):
    mapping = {
        "open":     Text("open",     style="bold green"),
        "filtered": Text("filtered", style="yellow"),
        "closed":   Text("closed",   style="dim red"),
    }
    return mapping.get(state, Text(state, style="dim"))


def display_rich(filepath, scan_info, hosts):
    fmt_badge = "[dim](xml)[/dim]" if scan_info["source"] == "xml" else "[dim](txt)[/dim]"
    console.print()
    console.rule(f"[bold cyan]📄 {filepath}  {fmt_badge}[/bold cyan]", style="cyan")

    meta = (
        f"[dim]CMD:[/dim]      [white]{scan_info['args']}[/white]\n"
        f"[dim]Started:[/dim]  {scan_info['start']}   "
        f"[dim]Duration:[/dim] {scan_info['elapsed']}   "
        f"[dim]Nmap:[/dim] v{scan_info['version']}"
    )
    console.print(Panel(meta, title="[bold]Scan Info[/bold]", border_style="dim"))

    if not hosts:
        console.print("[yellow]⚠  No active hosts found.[/yellow]\n")
        return

    console.print(f"\n[bold green]Active hosts: {len(hosts)}[/bold green]\n")

    for host in hosts:
        ip  = host["addrs"].get("ipv4", host["addrs"].get("ipv6", host.get("_raw_host", "?")))
        mac = host["addrs"].get("mac", "")
        hn  = ", ".join(host["hostnames"]) if host["hostnames"] else ""

        header = f"[bold yellow]{ip}[/bold yellow]"
        if hn:
            header += f"  [cyan]({hn})[/cyan]"
        if mac:
            header += f"  [dim]MAC: {mac}[/dim]"
        if host["os"]:
            best = host["os"][0]
            header += f"\n[magenta]OS: {best['name']}  ({best['accuracy']}% confidence)[/magenta]"

        console.print(Panel(header, border_style="yellow", padding=(0, 1)))

        if not host["ports"]:
            console.print("  [dim]No port information available.[/dim]\n")
            continue

        table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim")
        table.add_column("Port",     style="bold cyan", width=12)
        table.add_column("State",    width=11)
        table.add_column("Service",  style="green",     width=16)
        table.add_column("Version / Product",           width=36)
        table.add_column("NSE Scripts",                 width=40)

        for p in sorted(host["ports"], key=lambda x: int(x["portid"])):
            scripts_lines = []
            for sc in p["scripts"]:
                out = sc["output"][:80].replace("\n", " ")
                scripts_lines.append(f"[bold]{sc['id']}[/bold]: {out}")

            table.add_row(
                f"{p['portid']}/{p['proto']}",
                _state_rich(p["state"]),
                p["service"] or "[dim]-[/dim]",
                p["version"] or "[dim]-[/dim]",
                "\n".join(scripts_lines) or "[dim]-[/dim]",
            )

        console.print(table)

        closed_n = sum(1 for p in host["ports"] if p["state"] != "open")
        if closed_n:
            console.print(f"  [dim]+ {closed_n} closed/filtered port(s)[/dim]")
        if host.get("uptime"):
            console.print(f"  [dim]Last reboot: {host['uptime']}[/dim]")
        console.print()


def display_plain(filepath, scan_info, hosts):
    SEP = "=" * 72
    sep = "-" * 72
    src = f"[{scan_info['source'].upper()}]"
    print(f"\n{SEP}")
    print(f"  {src}  {filepath}")
    print(f"  CMD:       {scan_info['args']}")
    print(f"  Started:   {scan_info['start']}  |  Duration: {scan_info['elapsed']}  |  Nmap v{scan_info['version']}")
    print(SEP)

    if not hosts:
        print("  [!] No active hosts found.\n")
        return

    print(f"  Active hosts: {len(hosts)}\n")

    for host in hosts:
        ip  = host["addrs"].get("ipv4", host["addrs"].get("ipv6", host.get("_raw_host", "?")))
        mac = host["addrs"].get("mac", "")
        hn  = ", ".join(host["hostnames"]) if host["hostnames"] else ""

        print(sep)
        line = f"  HOST: {ip}"
        if hn:  line += f"  ({hn})"
        if mac: line += f"  [MAC: {mac}]"
        print(line)

        if host["os"]:
            best = host["os"][0]
            print(f"  OS:   {best['name']} ({best['accuracy']}%)")

        if not host["ports"]:
            print("  No port information available.\n")
            continue

        print()
        print(f"  {'PORT':<14} {'STATE':<12} {'SERVICE':<16} VERSION")
        print(f"  {'-'*12:<14} {'-'*10:<12} {'-'*14:<16} {'-'*28}")

        for p in sorted(host["ports"], key=lambda x: int(x["portid"])):
            print(f"  {p['portid']+'/'+p['proto']:<14} {p['state']:<12} {p['service']:<16} {p['version']}")
            for sc in p["scripts"]:
                out = sc["output"][:60].replace("\n", " ")
                print(f"  {'':14}   [NSE] {sc['id']}: {out}")
        print()


#  FORMAT DETECTION & MAIN

def detect_format(filepath):
    """Detect file format by extension; fall back to content sniffing."""
    if Path(filepath).suffix.lower() == ".xml":
        return "xml"
    try:
        with open(filepath, "r", errors="replace") as f:
            head = f.read(512)
        if head.lstrip().startswith("<?xml") or "<nmaprun" in head:
            return "xml"
    except Exception:
        pass
    return "txt"


def process_file(filepath):
    fmt = detect_format(filepath)
    try:
        if fmt == "xml":
            scan_info, hosts = parse_xml(filepath)
        else:
            scan_info, hosts = parse_txt(filepath)
    except ET.ParseError as e:
        msg = f"[!] XML parse error in '{filepath}': {e}"
        (console.print(f"[red]{msg}[/red]") if HAS_RICH else print(msg))
        return False
    except Exception as e:
        msg = f"[!] Error processing '{filepath}': {e}"
        (console.print(f"[red]{msg}[/red]") if HAS_RICH else print(msg))
        return False

    if HAS_RICH:
        display_rich(filepath, scan_info, hosts)
    else:
        display_plain(filepath, scan_info, hosts)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nmap_reader.py <file> [...]")
        print()
        print("  Formats:    .xml  |  .txt / .nmap / plain text")
        print("  Wildcards:  python3 nmap_reader.py *.xml *.txt")
        print()
        print("  How to generate the files:")
        print("    nmap -sV -sC -oX scan.xml <target>   # XML only")
        print("    nmap -sV -sC -oN scan.txt <target>   # Plain text only")
        print("    nmap -sV -sC -oA scan <target>       # Both at once")
        sys.exit(1)

    if not HAS_RICH:
        print("[!] Install rich for colored output: pip install rich\n")

    errors = 0
    for f in sys.argv[1:]:
        if not Path(f).exists():
            msg = f"[!] File not found: {f}"
            (console.print(f"[red]{msg}[/red]") if HAS_RICH else print(msg))
            errors += 1
            continue
        if not process_file(f):
            errors += 1

    sys.exit(errors)


if __name__ == "__main__":
    main()