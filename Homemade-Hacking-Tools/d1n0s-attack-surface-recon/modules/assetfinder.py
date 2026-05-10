import subprocess
import shutil

def _is_available() -> bool:
    return shutil.which("assetfinder") is not None

def find(domain: str) -> list[str]:
    """
    Ejecuta assetfinder para encontrar subdominios.
    Devuelve lista de FQDNs encontrados.
    """
    if not _is_available():
        print("[assetfinder] assetfinder no encontrado en PATH")
        return []
    try:
        result = subprocess.run(
            ["assetfinder", "--subs-only", domain],
            capture_output=True, text=True, timeout=120
        )
        subdomains = []
        for line in result.stdout.splitlines():
            line = line.strip().lower()
            if line.endswith(f".{domain}") or line == domain:
                subdomains.append(line)
        return sorted(set(subdomains))
    except subprocess.TimeoutExpired:
        print(f"[assetfinder] Timeout para {domain}")
        return []
    except Exception as e:
        print(f"[assetfinder] Error: {e}")
        return []
