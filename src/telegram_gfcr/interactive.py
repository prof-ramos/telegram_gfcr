"""REPL interativo com prompt_toolkit."""

import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import get_settings
from .core.client import shutdown_pool

# Comandos disponíveis no modo interativo
COMMANDS = {
    "help": "Exibe esta ajuda",
    "list": "Lista grupos, conversas e canais",
    "backup": "Faz backup: backup <id> [--media]",
    "forward": "Encaminha: forward <origem> <destino>",
    "search": "Busca: search <termo> [--id <id>]",
    "leave": "Sai de um grupo: leave <id>",
    "clear": "Limpa a tela",
    "exit": "Encerra o CLI",
}

# Estilo do prompt
STYLE = Style.from_dict(
    {
        "prompt": "bold cyan",
        "command": "bold green",
    }
)


def show_banner(console: Console) -> None:
    """Exibe banner de boas-vindas."""
    console.print(
        Panel.fit(
            f"[bold blue]🤖 Telegram GFCR[/] [dim]v{__version__}[/]\n"
            "[dim]Digite[/] [bold green]help[/] [dim]para ver comandos disponíveis[/]",
            border_style="blue",
        )
    )


def show_help(console: Console) -> None:
    """Exibe tabela de comandos disponíveis."""
    table = Table(title="Comandos Disponíveis", show_header=True, header_style="bold cyan")
    table.add_column("Comando", style="green")
    table.add_column("Descrição")

    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)

    console.print(table)


def process_command(cmd: str, console: Console) -> bool:
    """
    Processa comando do usuário.

    Returns:
        True se deve continuar o loop, False para sair.
    """
    parts = cmd.strip().split()
    if not parts:
        return True

    command = parts[0].lower()
    args = parts[1:]

    match command:
        case "exit" | "quit" | "q":
            console.print("[dim]👋 Até logo![/]")
            return False

        case "help" | "h" | "?":
            show_help(console)

        case "clear" | "cls":
            console.clear()
            show_banner(console)

        case "list":
            from .commands.list import run_list

            entity_type = args[0] if args else "all"
            run_list(entity_type)

        case "backup":
            if not args:
                console.print("[red]Uso: backup <id> [--media][/]")
            else:
                from .commands.backup import run_backup

                try:
                    entity_id = int(args[0])
                except ValueError:
                    console.print("[red]ID inválido: use um número[/]")
                    return True
                media = "--media" in args or "-m" in args
                run_backup(entity_id, None, media)

        case "forward":
            if len(args) < 2:
                console.print("[red]Uso: forward <origem> <destino>[/]")
            else:
                from .commands.forward import run_forward

                try:
                    source_id = int(args[0])
                    dest_id = int(args[1])
                except ValueError:
                    console.print("[red]IDs inválidos: use números[/]")
                    return True
                run_forward(source_id, dest_id, 100)

        case "search":
            if not args:
                console.print("[red]Uso: search <termo> [--id <id>] [--limit <n>][/]")
            else:
                from .commands.search import run_search

                query = args[0]
                entity_id = None
                limit = 20

                if "--id" in args:
                    idx = args.index("--id")
                    if idx + 1 < len(args):
                        try:
                            entity_id = int(args[idx + 1])
                        except ValueError:
                            console.print("[red]ID inválido[/]")
                            return True

                if "--limit" in args:
                    idx = args.index("--limit")
                    if idx + 1 < len(args):
                        try:
                            limit = int(args[idx + 1])
                        except ValueError:
                            console.print("[red]Limite inválido[/]")
                            return True

                run_search(query, entity_id, limit)

        case "leave":
            if not args:
                console.print("[red]Uso: leave <id>[/]")
            else:
                from .commands.leave import run_leave

                try:
                    entity_id = int(args[0])
                except ValueError:
                    console.print("[red]ID inválido: use um número[/]")
                    return True
                run_leave(entity_id, confirm=False)

        case _:
            console.print(f"[yellow]⚠️ Comando desconhecido:[/] {command}")
            console.print("[dim]Digite 'help' para ver comandos disponíveis[/]")

    return True


def start_session() -> None:
    """Inicia sessão interativa REPL."""
    console = Console()
    settings = get_settings()

    # Configurar histórico de comandos
    history_file = settings.ensure_data_dir() / "history.txt"

    session: PromptSession[str] = PromptSession(
        completer=WordCompleter(list(COMMANDS.keys()), ignore_case=True),
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
        style=STYLE,
        enable_history_search=True,
    )

    show_banner(console)

    try:
        while True:
            try:
                cmd = session.prompt("telegram> ")
                if not process_command(cmd, console):
                    break
            except KeyboardInterrupt:
                console.print("\n[dim]Use 'exit' para sair[/]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Erro: {e}[/]")
    finally:
        import contextlib

        # Cleanup: desconectar pool
        console.print("[dim]Fechando conexão...[/]")
        with contextlib.suppress(Exception):
            asyncio.run(shutdown_pool())
