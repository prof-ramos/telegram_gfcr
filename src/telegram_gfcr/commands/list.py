"""Comando para listar entidades."""

from rich.console import Console
from rich.table import Table

from ..core.client import get_client, run_async
from ..core.errors import AuthenticationError, TelegramError

console = Console()


def run_list(entity_type: str = "all") -> None:
    """Lista grupos, conversas e canais."""

    async def _list() -> list[tuple[int, str, str, int]]:
        async with get_client() as client:
            return await client.get_dialogs(entity_type)

    console.print(f"[blue]📂 Listando entidades ({entity_type})...[/]")

    try:
        dialogs = run_async(_list())
    except AuthenticationError as e:
        console.print(f"[yellow]⚠️ {e}[/]")
        return
    except TelegramError as e:
        console.print(f"[red]Erro: {e}[/]")
        return

    if not dialogs:
        console.print("[yellow]Nenhuma entidade encontrada[/]")
        return

    table = Table(title=f"Entidades ({len(dialogs)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Nome")
    table.add_column("Tipo", style="green")
    table.add_column("Não lidas", justify="right")

    type_emoji = {
        "user": "👤",
        "group": "👥",
        "supergroup": "👥",
        "channel": "📢",
        "unknown": "❓",
    }

    for dialog_id, name, dtype, unread in dialogs:
        emoji = type_emoji.get(dtype, "❓")
        table.add_row(
            str(dialog_id),
            name[:40] + "..." if len(name) > 40 else name,
            f"{emoji} {dtype}",
            str(unread) if unread > 0 else "-",
        )

    console.print(table)
