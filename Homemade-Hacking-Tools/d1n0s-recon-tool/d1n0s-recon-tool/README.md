# 🦖 D1n0s-recon-tool

A modular asset reconnaissance tool for Red Team exercises. Automates the full process of identifying and prioritizing the attack surface of a target organization.

---

## Reconnaissance flow

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
├── config.py                # Global config: timeouts, API keys (loaded from .env)
│
├── modules/
│   ├── company.py           # Company analysis: subsidiaries, former names, providers
│   ├── asn.py               # ASN identification via BGP Hurricane
│   ├── domains.py           # Domains: reverse CIDR, reverse NS/MX
│   ├── subdomains.py        # Subdomains: crt.sh, DNS brute-force
│   ├── enumerate.py         # Enumeration: Shodan, httpx, Nuclei
│   └── prioritize.py        # Asset prioritization based on interest criteria
│
├── utils.py                 # Shared HTTP helper (rotating user-agent) + DNS helper
├── .env                     # API keys (not committed)
├── .gitignore
├── requirements.txt
│
└── output/
    ├── excel_writer.py      # Fills Attack_Surface.xlsx with results
    └── console.py           # Pretty print with rich
```

---

## Modules

### `modules/company.py`
Starting point of the reconnaissance. Given an organization name, searches for related entities across multiple public sources.

| Source | Method | Key required |
|---|---|---|
| Wikipedia API | Search by org name | No |
| Wikidata API | Entity search | No |
| DuckDuckGo Instant Answer | Related topics | No |
| OpenCorporates | Company registry search | Yes — discarded (paid) |

### `modules/asn.py`
Identifies autonomous systems registered under the organization name.

| Source | Method | Key required |
|---|---|---|
| BGP Hurricane | HTML scraping of bgp.he.net/search | No |
| WhoisXMLAPI | Reverse Netblocks by org name | Yes — discarded (IP blocked) |

### `modules/domains.py`
Identifies main domains from the discovered ASNs and IP ranges.

| Technique | Tool |
|---|---|
| Reverse CIDR / PTR | bgp.tools |
| Reverse NS | viewdns.info/reversens |
| Reverse MX | viewdns.info/reversemx |

### `modules/subdomains.py`
Passive and active subdomain enumeration for each identified domain.

- **Passive:** crt.sh, DNSdumpster
- **Brute-force:** DNS resolution with wordlist (SecLists — `bitquark-subdomains-top100000.txt`)

### `modules/enumerate.py`
Attack surface enumeration across all discovered assets.

- Per-IP lookup via Shodan free tier (`api.host()`)
- Live web host validation with httpx
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
Dumps results into `Attack_Surface.xlsx`:

| Sheet | Fields |
|---|---|
| Companies | Name, Source |
| IP Ranges | ASN, Name, Source, Country |
| Domains | Domain, Source, Reverse NS, Reverse MX... |
| Subdomains | FQDN, Parent Domain, IP, Resolution, EyeWitness, Nuclei |

### `output/console.py`
Console output using `rich`. Displays results per phase with colors and tables.

---

## Required APIs

| Service | Key required | Free tier | Status |
|---|---|---|---|
| Shodan | Yes | Yes (limited to host lookup) | ✅ In use |
| BGP Hurricane | No | — | ✅ In use |
| Wikipedia / Wikidata | No | — | ✅ In use |
| DuckDuckGo | No | — | ✅ In use |
| WhoisXMLAPI | Yes | Yes | ❌ Discarded — IP blocked |
| OpenCorporates | Yes | No | ❌ Discarded — paid plan |

API keys are loaded from `.env`:

```
SHODAN_API_KEY=your_key_here
```

---

## Installation

```bash
git clone https://github.com/D1n0/d1n0-recon-tool
cd d1n0-recon-tool
pip install -r requirements.txt
```
> **Kali Linux:** use `pip3` and `python3` explicitly. `pip` and `python` point to Python 2.7.

```bash
pip3 install -r requirements.txt --break-system-packages
python3 main.py -t "Target Organization"
```


**Main dependencies:**
```
requests
dnspython
ipwhois
shodan
openpyxl
rich
beautifulsoup4
python-dotenv
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
| `config.py` | ✅ Done |
| `utils.py` | ✅ Done |
| `output/console.py` | ✅ Done |
| `output/excel_writer.py` | ✅ Done |
| `modules/company.py` | ⚠️ Working — noise filtering pending |
| `modules/asn.py` | ✅ Done |
| `modules/domains.py` | ⬜ Pending |
| `modules/subdomains.py` | ⬜ Pending |
| `modules/enumerate.py` | ⬜ Pending |
| `modules/prioritize.py` | ⬜ Pending |

---

*d1n0 · Ethical Hacking 2025/26*