import argparse
import os
import sys
from config import HTTP_TIMEOUT, DNS_TIMEOUT, SHODAN_API_KEY, WHOISXML_API_KEY

from modules.company import get_company_info
from modules.asn import get_asn_info
#from modules.domains import get_domains_info
#from modules.subdomains import get_subdomains_info
#from modules.enumerate import get_enumerate_info
#from modules.prioritize import get_prioritize_info


MODULES = {
    "company":    get_company_info,
    "asn":        get_asn_info,
 #   "domains":    get_domains_info,
  #  "subdomains": get_subdomains_info,
   # "enumerate":  get_enumerate_info,
    #"prioritize": get_prioritize_info,
}

def parse_args():
    parser = argparse.ArgumentParser(
        prog="d1n0-recon",
        description="Reconocimiento de activos automatizado — Red Team",
    )
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("--only", choices=MODULES.keys(), default=None)
    parser.add_argument("--output", default="Attack_Surface.xlsx")
    parser.add_argument("--no-excel", action="store_true")
    return parser.parse_args()


def run(args):
    from output.console import banner, section

    banner(args.target)

    results = {
        "target":     args.target,
        "companies":  [],
        "asns":       [],
        "ranges":     [],
        "domains":    [],
        "subdomains": [],
        "enumerate":  [],
    }

    modules_to_run = [args.only] if args.only else MODULES.keys()

    for mod_name in modules_to_run:
        section(mod_name)
        try:
            results = MODULES[mod_name](results)
        except Exception as e:
            import traceback
            traceback.print_exc()

    if not args.no_excel:
        from output.excel import write
        write(results, args.output)

    return results


if __name__ == "__main__":
    args = parse_args()
    run(args)