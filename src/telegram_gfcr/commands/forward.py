"""Comando para encaminhar mensagens."""

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.client import get_client, run_async
from ..core.errors import RateLimitError, TelegramError, handle_telethon_errors, retry_on_flood

console = Console()


@retry_on_flood(max_retries=5)
@handle_telethon_errors("forward_message")
async def _forward_with_retry(client, dest_id: int, message) -> None:
    """Encaminha mensagem com retry automático em FloodWait."""
    await client.forward_messages(dest_id, message)


def run_forward(source_id: int, dest_id: int, limit: int) -> None:
    """Encaminha mensagens entre entidades."""

    async def _forward() -> int:
        async with get_client() as client:
            count = 0

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Encaminhando mensagens...", total=None)

                async for message in client.client.iter_messages(source_id, limit=limit):
                    try:
                        await _forward_with_retry(client.client, dest_id, message)
                        count += 1
                        progress.update(task, description=f"Encaminhando... ({count}/{limit})")
                    except RateLimitError:
                        logger.warning(f"Mensagem {message.id} pulada após max retries")
                    except Exception as e:
                        logger.warning(f"Mensagem {message.id} não encaminhada: {e}")

            return count

    console.print(f"[blue]📤 Encaminhando de {source_id} para {dest_id}...[/]")

    try:
        total = run_async(_forward())
        console.print(f"[green]✓ {total} mensagens encaminhadas![/]")
    except RateLimitError as e:
        console.print(f"[yellow]⚠️ Rate limit: {e}[/]")
    except TelegramError as e:
        console.print(f"[red]Erro: {e}[/]")
