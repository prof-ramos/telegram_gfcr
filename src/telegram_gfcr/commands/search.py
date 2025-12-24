"""Comando para buscar mensagens."""

from rich.console import Console
from rich.table import Table

from ..core.client import get_client, run_async
from ..core.errors import RateLimitError, TelegramError, handle_telethon_errors

console = Console()


@handle_telethon_errors("search_messages")
async def _search_async(query: str, entity_id: int | None = None, limit: int = 20) -> list:
    """Busca mensagens de forma assíncrona."""
    async with get_client() as client:
        results = []
        # Se entity_id for None, busca globalmente (se suportado pelo wrapper/telethon)
        # Caso contrário, busca na entidade específica
        async for message in client.client.iter_messages(entity_id, search=query, limit=limit):
            results.append(message)
        return results


def run_search(query: str, entity_id: int | None = None, limit: int = 20) -> None:
    """Executa busca de mensagens."""
    console.print(f"[blue]🔍 Buscando por '[bold]{query}[/]'...[/]")
    if entity_id:
        console.print(f"[dim]No chat: {entity_id}[/]")

    try:
        messages = run_async(_search_async(query, entity_id, limit))
    except RateLimitError as e:
        console.print(f"[yellow]⚠️ Rate limit: {e}[/]")
        return
    except TelegramError as e:
        console.print(f"[red]Erro na busca: {e}[/]")
        return

    if not messages:
        console.print("[yellow]Nenhuma mensagem encontrada[/]")
        return

    table = Table(
        title=f"Resultados da Busca ({len(messages)})",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Data", style="dim")
    table.add_column("De", style="green")
    table.add_column("Mensagem")

    for msg in messages:
        sender = "Desconhecido"
        if msg.sender:
            sender = (
                getattr(msg.sender, "first_name", "")
                or getattr(msg.sender, "title", "Sistema")
            )

        text = msg.text or "[Mídia/Sem texto]"
        if len(text) > 100:
            text = text[:97] + "..."

        table.add_row(
            msg.date.strftime("%Y-%m-%d %H:%M"),
            sender,
            text.replace("\n", " ")
        )

    console.print(table)
