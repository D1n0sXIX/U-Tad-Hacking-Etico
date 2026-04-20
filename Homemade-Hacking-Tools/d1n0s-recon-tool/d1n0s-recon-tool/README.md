# 🦖 D1n0s-recon-tool

A modular asset reconnaissance tool for Red Team exercises.
Automates the full process of identifying and prioritizing the attack surface of a target organization.

---

## Reconnaissance Flow

```
Company → ASN / IP Ranges → Domains → Subdomains → Enumeration → Prioritization
```

Each module receives the output of the previous one and dumps results to the console and the attack surface Excel file.

---

## Project structure

```
d1n0-recon-tool/
│
├── main.py                  # Entry point. Argparse, global timeouts, main flow
│
├── modules/
│   ├── company.py           # Company analysis: subsidiaries, former names, providers
│   ├── asn.py               # ASN and IP range identification (BGP HE, RIRs, WhoisXMLAPI)
│   ├── domains.py           # Domains: reverse CIDR, reverse WHOIS, reverse NS/MX
│   ├── subdomains.py        # Subdomains: crt.sh, Amass, Assetfinder, DNS brute-force
│   ├── enumerate.py         # Enumeration: Shodan, httpx, Nuclei, EyeWitness
│   └── prioritize.py        # Asset prioritization based on interest criteria
│
├── utils.py                 # Shared HTTP helper (rotating user-agent) + DNS helper
│
└── output/
    ├── excel_writer.py      # Fills Attack_Surface.xlsx with results
    └── console.py           # Pretty print with rich
```

---

## Modules

### `modules/company.py`
Starting point of the reconnaissance. Given an organization name, it searches for:
- Former names and variants in other countries
- Subsidiaries and owned companies
- Relevant providers

### `modules/asn.py`
Identifies autonomous systems and IP ranges registered under the organization.

| Source | Method |
|---|---|
| BGP Hurricane | `http://bgp.he.net/` — ASNs + CIDR ranges |
| RIRs (RIPE…) | WHOIS query by org name |
| WhoisXMLAPI | Reverse Netblocks — ranges without own ASN |
| Amass | `amass intel -org <org>` |

### `modules/domains.py`
Identifies main domains from the discovered IP ranges.

| Technique | Tool |
|---|---|
| Reverse CIDR / PTR | IPIP, WhoisXMLAPI, bgp.tools |
| Reverse WHOIS | WhoisXMLAPI |
| Reverse NS | viewdns.info/reversens |
| Reverse MX | viewdns.info/reversemx |

### `modules/subdomains.py`
Passive and active subdomain enumeration for each identified domain.

- **Passive:** crt.sh, VirusTotal, SecurityTrails, DNSdumpster
- **Tools:** Amass (`enum -passive`), Assetfinder
- **Brute-force:** mass DNS resolution with wordlist (SecLists — `bitquark-subdomains-top100000.txt`)

### `modules/enumerate.py`
Attack surface enumeration across all discovered assets.

- Passive port scanning via Shodan
- Live web host validation with httpx
- Screenshots with EyeWitness / GoWitness
- Automated vulnerability detection with Nuclei

### `modules/prioritize.py`
Asset prioritization based on Red Team interest criteria:

- Ranges with unusual or non-unified open ports
- Domains not found in public sources (potential Shadow IT)
- Web applications with outdated technologies
- Critical vulnerabilities detected by Nuclei

---

## Utilities

### `utils.py`
Functions shared across modules:
- `get(url)` — HTTP request with rotating user-agent, global timeout and error handling
- `resolve(hostname)` — DNS resolution from hostname to IP
- `ptr(ip)` — Reverse PTR lookup

---

## Output

### `output/excel_writer.py`
Dumps results into `Attack_Surface.xlsx` following the sheet structure:

| Sheet | Fields |
|---|---|
| Companies | Name, Source, RIRs, BGP HE, WhoisXML Netblock, WhoisXML Whois, Cloud_enum |
| IP Ranges | CIDR, Source, ASN, Amass, Nmap |
| Domains | Domain, Source, Amass Intel, Reverse NS, Reverse MX, Amass Enum, Assetfinder, Shodan SSL, Subscan, SecurityTrails, Leaks |
| Subdomains | FQDN, Parent Domain, IP Address, Resolution, EyeWitness, Nuclei |

### `output/console.py`
Console output using `rich`. Displays results per phase with colors and tables.

---

## Required APIs

| Service | Key required | Free tier | Usage |
|---|---|---|---|
| Shodan | Yes | Yes (limited) | Passive port enumeration |
| WhoisXMLAPI | Yes | Yes | Reverse Netblocks, Reverse WHOIS |
| BGP Hurricane | No | — | ASNs and ranges |
| crt.sh | No | — | Subdomains via SSL certificates |
| viewdns.info | No | — | Reverse NS / MX |

API keys are set as environment variables:

```bash
export SHODAN_API_KEY="..."
export WHOISXML_API_KEY="..."
```

---

## Installation

```bash
git clone https://github.com/D1n0/d1n0-recon-tool
cd d1n0-recon-tool
pip install -r requirements.txt
```

**Main dependencies:**
```
requests
dnspython
ipwhois
shodan
openpyxl
rich
```

---

## Usage

```bash
# Full reconnaissance
python main.py -t "Target Organization"

# Single module
python main.py -t "Target Organization" --only asn
python main.py -t "Target Organization" --only subdomains

# Available modules: company, asn, domains, subdomains, enumerate, prioritize

# Custom Excel output path
python main.py -t "Target Organization" --output Attack_Surface.xlsx

# Console only, no Excel
python main.py -t "Target Organization" --no-excel
```

---

## Development status

| File | Status |
|---|---|
| `main.py` | ✅ Done |
| `utils.py` | ✅ Done |
| `output/console.py` | ✅ Done |
| `output/excel_writer.py` | ✅ Done |
| `modules/company.py` | 🔧 In progress |
| `modules/asn.py` | ⬜ Pending |
| `modules/domains.py` | ⬜ Pending |
| `modules/subdomains.py` | ⬜ Pending |
| `modules/enumerate.py` | ⬜ Pending |
| `modules/prioritize.py` | ⬜ Pending |

---

*d1n0 · Ethical Hacking 2025/26*