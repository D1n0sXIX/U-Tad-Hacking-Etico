import subprocess
import shutil

CLOUD_ENUM_PATHS = [
    "cloud_enum",
    "/opt/cloud_enum/cloud_enum.py",
    "/usr/local/bin/cloud_enum",
]

def _get_binary() -> str | None:
    if shutil.which("cloud_enum"):
        return "cloud_enum"
    for path in CLOUD_ENUM_PATHS:
        try:
            result = subprocess.run(
                ["python3", path, "--help"],
                capture_output=True, timeout=5
            )
            if result.returncode in (0, 1):
                return f"python3 {path}"
        except Exception:
            continue
    return None

def scan(keywords: list[str]) -> list[str]:
    """
    Ejecuta cloud_enum sobre una lista de keywords.
    Devuelve lista de recursos cloud encontrados.
    """
    binary = _get_binary()
    if not binary:
        print("[cloud_enum] cloud_enum no encontrado")
        return []
    try:
        cmd_parts = binary.split()
        for kw in keywords:
            cmd_parts += ["-k", kw]
        result = subprocess.run(
            cmd_parts,
            capture_output=True, text=True, timeout=300
        )
        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and ("http" in line or "s3" in line.lower() or "blob" in line.lower()):
                findings.append(line)
        return findings
    except subprocess.TimeoutExpired:
        print("[cloud_enum] Timeout")
        return []
    except Exception as e:
        print(f"[cloud_enum] Error: {e}")
        return []
