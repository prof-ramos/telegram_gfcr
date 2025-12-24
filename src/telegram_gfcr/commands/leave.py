"""Comando para sair de grupos."""

import typer
from rich.console import Console

from ..core.client import get_client, run_async
from ..core.errors import TelegramError, TelegramPermissionError

console = Console()


def run_leave(entity_id: int, confirm: bool) -> None:
    """Sai de um grupo."""
    if not confirm and not typer.confirm(
        f"Tem certeza que deseja sair do grupo {entity_id}?"
    ):
        console.print("[yellow]Operação cancelada[/]")
        return

    async def _leave() -> bool:
        async with get_client() as client:
            entity = await client.client.get_entity(entity_id)
            await client.client.delete_dialog(entity)
            return True

    console.print(f"[blue]🚪 Saindo do grupo {entity_id}...[/]")

    try:
        run_async(_leave())
        console.print(f"[green]✓ Saiu do grupo {entity_id}[/]")
    except TelegramPermissionError as e:
        console.print(f"[yellow]⚠️ {e}[/]")
    except TelegramError as e:
        console.print(f"[red]Erro: {e}[/]")
