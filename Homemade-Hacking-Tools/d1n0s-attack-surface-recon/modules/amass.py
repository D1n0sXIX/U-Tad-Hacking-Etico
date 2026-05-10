import re
import subprocess
import shutil

DOMAIN_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}$')

def _is_available() -> bool:
    return shutil.which("amass") is not None

def intel(company: str, domain: str) -> list[str]:
    """
    Ejecuta amass intel para encontrar dominios asociados a la empresa.
    Devuelve lista de dominios encontrados.
    """
    if not _is_available():
        print("[amass] amass no encontrado en PATH")
        return []
    try:
        process = subprocess.Popen(
            ["amass", "intel", "-org", company, "-d", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        domains = []
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f"  [amass intel] {line}")
                if DOMAIN_RE.match(line):
                    domains.append(line)
        process.wait(timeout=120)
        return domains
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"[amass] intel timeout para {domain}")
        return []
    except Exception as e:
        print(f"[amass] Error intel: {e}")
        return []

def enum(domain: str) -> list[str]:
    """
    Ejecuta amass enum en modo pasivo para encontrar subdominios.
    Devuelve lista de FQDNs encontrados.
    """
    if not _is_available():
        print("[amass] amass no encontrado en PATH")
        return []
    try:
        process = subprocess.Popen(
            ["amass", "enum", "-passive", "-d", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        subdomains = []
        for line in process.stdout:
            line = line.strip().lower()
            if line:
                print(f"  [amass enum] {line}")
                if line.endswith(f".{domain}"):
                    subdomains.append(line)
        process.wait(timeout=600)
        return subdomains
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"[amass] enum timeout para {domain}")
        return []
    except Exception as e:
        print(f"[amass] Error enum: {e}")
        return []
