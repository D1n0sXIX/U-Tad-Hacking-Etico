from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def banner(target: str):
    console.print(Panel(
        f"[bold white]d1n0-recon-tool[/bold white]\n"
        f"[dim]Red Team Asset Reconnaissance[/dim]\n\n"
        f"[green]Target:[/green] [bold]{target}[/bold]",
        border_style="bright_blue",
        expand=False,
    ))
    console.print()


def section(name: str):
    console.rule(f"[bold bright_blue]{name.upper()}[/bold bright_blue]")
    console.print()


def info(msg: str):
    console.print(f"[cyan][*][/cyan] {msg}")


def success(msg: str):
    console.print(f"[green][+][/green] {msg}")


def warning(msg: str):
    console.print(f"[yellow][!][/yellow] {msg}")


def error(msg: str):
    console.print(f"[red][x][/red] {msg}")


def print_table(title: str, columns: list, rows: list):
    if not rows:
        warning(f"Sin resultados para: {title}")
        return

    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        border_style="dim",
        header_style="bold bright_blue",
        show_lines=False,
    )

    for col in columns:
        table.add_column(col, overflow="fold")

    for row in rows:
        table.add_row(*[str(v) for v in row])

    console.print(table)
    console.print()