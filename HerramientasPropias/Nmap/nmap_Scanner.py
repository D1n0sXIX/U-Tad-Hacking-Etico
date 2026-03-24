#!/usr/bin/env python3
# nmap_scanner.py
# D1n0 / Alejandro Mamán López-Mingo - INSO3A - 2024-06
# Partially made with Claude
"""
nmap_scanner.py — Interactive Nmap wrapper
  - Reads all flags, categories and profiles from nmap_flags.txt
  - Interactive menu built dynamically from that file
  - Save / load / delete custom profiles (written back to the .txt)
  - Choose output format at runtime
  - Auto-reads results with nmap_reader.py if available
"""
# libs
import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

# optional rich for better UI (not required)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
# globals
console   = Console() if HAS_RICH else None
BASE_DIR  = Path(__file__).parent
FLAGS_FILE  = BASE_DIR / "nmap_ScannerConf.txt"



#  PARSER — reads nmap_flags.txt

def load_flags_file():
    """
    Parse nmap_flags.txt and return:
        categories : dict  { "Category Name": [ (flag, description), ... ] }
        profiles   : dict  { "profile_name":  [flag1, flag2, ...] }
    """
    if not FLAGS_FILE.exists():
        err = f"[!] '{FLAGS_FILE}' not found. Create it next to nmap_scanner.py."
        (console.print(f"[red]{err}[/red]") if HAS_RICH else print(err))
        sys.exit(1)

    categories = {}
    profiles   = {}
    current_cat = None
    in_profiles = False

    for raw in FLAGS_FILE.read_text(errors="replace").splitlines():
        line = raw.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        # Section header
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if section.upper() == "PROFILES":
                in_profiles = True
                current_cat = None
            else:
                in_profiles = False
                current_cat = section
                categories.setdefault(current_cat, [])
            continue

        # Entry line — must contain |
        if "|" not in line:
            continue

        left, _, right = line.partition("|")
        left  = left.strip()
        right = right.strip()

        if in_profiles:
            # profile_name | flag1 flag2 ...
            profiles[left] = right.split()
        elif current_cat is not None:
            # flag | description
            categories[current_cat].append((left, right))

    return categories, profiles


def save_profile(name, flags):
    """Append or update a profile entry in nmap_flags.txt."""
    text   = FLAGS_FILE.read_text(errors="replace")
    lines  = text.splitlines()
    entry  = f"{name:<12}| {' '.join(flags)}"

    # Find [PROFILES] section and look for existing entry
    in_profiles = False
    new_lines   = []
    updated     = False

    for line in lines:
        stripped = line.strip()
        if stripped == "[PROFILES]":
            in_profiles = True
        if in_profiles and stripped and not stripped.startswith("#"):
            if "|" in stripped:
                existing_name = stripped.split("|")[0].strip()
                if existing_name == name:
                    new_lines.append(entry)
                    updated = True
                    continue
        new_lines.append(line)

    if not updated:
        # Add at end of [PROFILES] section or at end of file
        if "[PROFILES]" in text:
            new_lines.append(entry)
        else:
            new_lines += ["", "[PROFILES]", entry]

    FLAGS_FILE.write_text("\n".join(new_lines) + "\n")


def delete_profile(name):
    """Remove a profile entry from nmap_flags.txt."""
    lines     = FLAGS_FILE.read_text(errors="replace").splitlines()
    new_lines = []
    in_profiles = False

    for line in lines:
        stripped = line.strip()
        if stripped == "[PROFILES]":
            in_profiles = True
        if in_profiles and "|" in stripped and not stripped.startswith("#"):
            if stripped.split("|")[0].strip() == name:
                continue  # skip this line = delete it
        new_lines.append(line)

    FLAGS_FILE.write_text("\n".join(new_lines) + "\n")


#  UI HELPERS

def clear():
    os.system("clear")

def print_banner():
    if HAS_RICH:
        console.print(Panel(
            "[bold cyan]nmap_scanner.py[/bold cyan]  [dim]by D1n0[/dim]\n"
            "[dim]Flags and profiles loaded from  nmap_flags.txt[/dim]",
            border_style="cyan", padding=(0, 2)
        ))
    else:
        print("=" * 60)
        print("  nmap_scanner.py  by D1n0")
        print("  Flags loaded from nmap_flags.txt")
        print("=" * 60)

def ask(prompt, default=""):
    if HAS_RICH:
        val = Prompt.ask(f"[bold green]>[/bold green] {prompt}",
                         default=default if default else None)
        return val or default
    return input(f"> {prompt}: ").strip() or default

def confirm(prompt):
    if HAS_RICH:
        return Confirm.ask(f"[bold yellow]?[/bold yellow] {prompt}")
    return input(f"? {prompt} [y/N]: ").strip().lower() == "y"


#  FLAG SELECTION MENU

def print_flags_menu(categories):
    idx = 1
    index_map = {}  # global index → flag string

    if HAS_RICH:
        for cat, flags in categories.items():
            table = Table(
                box=box.SIMPLE, show_header=True, header_style="bold dim",
                title=f"[bold cyan]{cat}[/bold cyan]", title_justify="left",
            )
            table.add_column("#",    style="dim",        width=5)
            table.add_column("Flag", style="bold green", width=28)
            table.add_column("Description")
            for flag, desc in flags:
                table.add_row(str(idx), flag, desc)
                index_map[idx] = flag
                idx += 1
            console.print(table)
    else:
        for cat, flags in categories.items():
            print(f"\n  [{cat}]")
            for flag, desc in flags:
                print(f"  {idx:>4}.  {flag:<30} {desc}")
                index_map[idx] = flag
                idx += 1

    return index_map


def select_flags(categories):
    clear()
    print_banner()
    index_map = print_flags_menu(categories)

    if HAS_RICH:
        console.print("\n[dim]Enter numbers separated by spaces  (e.g. 1 3 7 12)[/dim]")
        console.print("[dim]You can also type custom flags inline  (e.g. --script vuln)[/dim]")
    else:
        print("\nEnter numbers (e.g. 1 3 7) — or type custom flags directly")

    raw = ask("Select flags").split()

    selected = []
    custom   = []

    for token in raw:
        if token.isdigit():
            n = int(token)
            if n in index_map:
                flag = index_map[n]
                if flag not in selected:
                    selected.append(flag)
            else:
                warn = f"  ! Index {n} out of range — skipped"
                (console.print(f"[yellow]{warn}[/yellow]") if HAS_RICH else print(warn))
        else:
            custom.append(token)

    extra = ask("Additional custom flags (blank to skip)", "")
    if extra.strip():
        custom.extend(extra.strip().split())

    return selected + custom


#  OUTPUT SELECTION

def select_output(target):
    if HAS_RICH:
        console.print("\n[bold]Output format:[/bold]")
        console.print("  [cyan]1[/cyan]  XML only  (readable with nmap_reader.py)")
        console.print("  [cyan]2[/cyan]  Text only (.txt)")
        console.print("  [cyan]3[/cyan]  Both XML + text")
        console.print("  [cyan]4[/cyan]  Screen only — no file saved")
    else:
        print("\nOutput format:")
        print("  1  XML only")
        print("  2  Text only (.txt)")
        print("  3  Both XML + text")
        print("  4  Screen only — no file saved")

    choice = ask("Choice", "1")

    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_t  = target.replace("/", "-").replace(" ", "_")
    stem    = f"scan_{safe_t}_{ts}"

    xml_path = txt_path = None
    output_flags = []

    if choice in ("1", "2", "3"):
        out_dir = ask("Output directory", ".")
        base    = str(Path(out_dir) / stem)
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        if choice == "1":
            xml_path     = base + ".xml"
            output_flags = ["-oX", xml_path]
        elif choice == "2":
            txt_path     = base + ".txt"
            output_flags = ["-oN", txt_path]
        elif choice == "3":
            xml_path     = base + ".xml"
            txt_path     = base + ".txt"
            output_flags = ["-oX", xml_path, "-oN", txt_path]

    return output_flags, xml_path, txt_path


#  PROFILES MENU

def profiles_menu(profiles):
    clear()
    print_banner()

    if HAS_RICH:
        console.print("[bold]Saved profiles:[/bold]\n")
        if profiles:
            table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
            table.add_column("Name",  style="bold cyan", width=18)
            table.add_column("Flags")
            for name, flags in profiles.items():
                table.add_row(name, " ".join(flags))
            console.print(table)
        else:
            console.print("[dim]  No profiles saved yet.[/dim]")

        console.print("\n  [cyan]1[/cyan]  Load a profile")
        console.print("  [cyan]2[/cyan]  Delete a profile")
        console.print("  [cyan]3[/cyan]  Back")
    else:
        print("Saved profiles:\n")
        if profiles:
            for name, flags in profiles.items():
                print(f"  {name:<20} {' '.join(flags)}")
        else:
            print("  No profiles saved yet.")
        print("\n  1  Load a profile\n  2  Delete a profile\n  3  Back")

    choice = ask("Choice", "3")

    if choice == "1" and profiles:
        name = ask("Profile name")
        if name in profiles:
            return profiles[name]
        warn = f"Profile '{name}' not found."
        (console.print(f"[red]{warn}[/red]") if HAS_RICH else print(warn))

    elif choice == "2" and profiles:
        name = ask("Profile name to delete")
        if name in profiles:
            delete_profile(name)
            ok = f"Profile '{name}' deleted."
            (console.print(f"[green]{ok}[/green]") if HAS_RICH else print(ok))
        else:
            warn = f"Profile '{name}' not found."
            (console.print(f"[red]{warn}[/red]") if HAS_RICH else print(warn))

    return None


#  NMAP RUNNER

def run_nmap(target, flags, output_flags):
    cmd = ["nmap"] + flags + output_flags + [target]

    if HAS_RICH:
        console.print(f"\n[bold dim]Running:[/bold dim] [white]{' '.join(cmd)}[/white]\n")
        console.rule("[dim]nmap output[/dim]", style="dim")
    else:
        print(f"\nRunning: {' '.join(cmd)}\n" + "-" * 60)

    try:
        subprocess.run(cmd, text=True)
    except FileNotFoundError:
        err = "[!] nmap not found — install with: sudo apt install nmap"
        (console.print(f"[red]{err}[/red]") if HAS_RICH else print(err))



#  MAIN MENU AND PROGRAM ENTRY POINT
def main():
    while True:
        # Reload file every loop so changes to nmap_flags.txt are picked up live
        categories, profiles = load_flags_file()

        clear()
        print_banner()

        if HAS_RICH:
            console.print("\n  [cyan]1[/cyan]  New scan")
            console.print("  [cyan]2[/cyan]  Load a saved profile")
            console.print("  [cyan]3[/cyan]  Manage profiles")
            console.print("  [cyan]4[/cyan]  Exit\n")
        else:
            print("\n  1  New scan\n  2  Load a saved profile\n  3  Manage profiles\n  4  Exit\n")

        choice = ask("Choice", "1")

        if choice in ("1", "2"):
            target = ask("Target IP / range  (e.g. 192.168.1.1  or  192.168.1.0/24)")
            if not target:
                continue

            if choice == "1":
                flags = select_flags(categories)
            else:
                loaded = profiles_menu(profiles)
                if loaded is None:
                    continue
                flags = loaded

            if HAS_RICH:
                console.print(f"\n[bold]Flags:[/bold] [green]{' '.join(flags) or '(none)'}[/green]")
            else:
                print(f"\nFlags: {' '.join(flags) or '(none)'}")

            # Offer to save as new profile
            if choice == "1" and flags and confirm("Save this flag set as a profile?"):
                name = ask("Profile name")
                save_profile(name, flags)
                ok = f"Profile '{name}' saved to nmap_flags.txt."
                (console.print(f"[green]{ok}[/green]") if HAS_RICH else print(ok))

            output_flags, xml_path, txt_path = select_output(target)
            run_nmap(target, flags, output_flags)
            input("\nPress Enter to continue...")

        elif choice == "3":
            profiles_menu(profiles)
            input("\nPress Enter to continue...")

        elif choice == "4":
            break


if __name__ == "__main__":
    main()
