import subprocess
import shutil

def _is_available() -> bool:
    return shutil.which("nmap") is not None

def ping_sweep(cidr: str) -> list[str]:
    """
    Ejecuta nmap -sn sobre un CIDR.
    Devuelve lista de IPs activas encontradas.
    """
    if not _is_available():
        print("[nmap] nmap no encontrado en PATH")
        return []
    try:
        result = subprocess.run(
            ["nmap", "-sn", "-T4", cidr],
            capture_output=True, text=True, timeout=300
        )
        active_ips = []
        for line in result.stdout.splitlines():
            if "Nmap scan report for" in line:
                parts = line.split()
                ip = parts[-1].strip("()")
                active_ips.append(ip)
        return active_ips
    except subprocess.TimeoutExpired:
        print(f"[nmap] Timeout para {cidr}")
        return []
    except Exception as e:
        print(f"[nmap] Error: {e}")
        return []
