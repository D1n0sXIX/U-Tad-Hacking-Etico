import argparse
import os
import sys

# Timeouts
HTTP_TIMEOUT = 10   # segundos para requests HTTP
DNS_TIMEOUT  = 5    # segundos para consultas DNS

#  API Keys
SHODAN_API_KEY   = os.getenv("SHODAN_API_KEY", "")
WHOISXML_API_KEY = os.getenv("WHOISXML_API_KEY", "")

#  Modulos disponibles
MODULES = ["company", "asn", "domains", "subdomains", "enumerate"]

# Funciones principales
def parse_args():
    parser = argparse.ArgumentParser(
        prog="d1n0-recon",
        description="Reconocimiento de activos automatizado — Red Team",
    )
    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Nombre de la organización objetivo (ej: 'Telefonica')"
    )
    parser.add_argument(
        "--only",
        choices=MODULES,
        default=None,
        help="Ejecutar solo un módulo concreto"
    )
    parser.add_argument(
        "--output",
        default="Attack_Surface.xlsx",
        help="Ruta del Excel de salida (default: Attack_Surface.xlsx)"
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="No escribir resultados en Excel, solo consola"
    )
    return parser.parse_args()


def run(args):
    from output.console import banner, section

    banner(args.target)

    # Resultados acumulados que se pasan entre modulos
    results = {
        "target":     args.target,
        "companies":  [],   # company.py
        "asns":       [],   # asn.py
        "ranges":     [],   # asn.py
        "domains":    [],   # domains.py
        "subdomains": [],   # subdomains.py
        "enumerate":  [],   # enumerate.py
    }

    modules_to_run = [args.only] if args.only else MODULES

    for mod_name in modules_to_run:
        section(mod_name)
        try:
            mod = __import__(f"modules.{mod_name}", fromlist=[mod_name])
            results = mod.run(results)
        except Exception as e:
            print(f"[!] Error en módulo {mod_name}: {e}")

    if not args.no_excel:
        from output.excel_writer import write
        write(results, args.output)

    return results


if __name__ == "__main__":
    args = parse_args()
    run(args)