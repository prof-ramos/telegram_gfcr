"""Comando de backup de conversas."""

from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.client import get_client, run_async
from ..core.errors import RateLimitError, TelegramError, handle_telethon_errors, retry_on_flood

console = Console()


@retry_on_flood(max_retries=3)
@handle_telethon_errors("download_media")
async def _download_media_with_retry(message, media_dir: Path) -> None:
    """Download de mídia com retry automático em FloodWait."""
    await message.download_media(file=str(media_dir))


def run_backup(entity_id: int, output: str | None, media: bool) -> None:
    """Faz backup de uma conversa ou grupo."""
    output_path = Path(output) if output else Path.cwd() / "backups" / str(entity_id)
    output_path.mkdir(parents=True, exist_ok=True)

    async def _backup() -> int:
        async with get_client() as client:
            messages_file = output_path / "messages.jsonl"
            count = 0
            batch: list[str] = []
            batch_size = 100

            def _flush_batch() -> None:
                """Escreve batch de mensagens no arquivo."""
                nonlocal batch
                if batch:
                    with messages_file.open("a", encoding="utf-8") as f:
                        f.write("\n".join(batch) + "\n")
                    batch = []

            # Criar diretório de mídia uma única vez, fora do loop
            media_dir: Path | None = None
            if media:
                media_dir = output_path / "media"
                media_dir.mkdir(exist_ok=True)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Baixando mensagens de {entity_id}...", total=None
                )

                async for message in client.client.iter_messages(entity_id):
                    # Adicionar ao batch (em memória)
                    batch.append(message.to_json())

                    # Flush quando batch atinge o limite
                    if len(batch) >= batch_size:
                        _flush_batch()
                        logger.debug(f"Batch de {batch_size} mensagens salvo")

                    # Download de mídia se solicitado
                    if media_dir and message.media:
                        try:
                            await _download_media_with_retry(message, media_dir)
                            logger.debug(f"Mídia baixada: msg {message.id}")
                        except RateLimitError:
                            logger.warning(
                                f"Mídia msg {message.id} pulada após max retries"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Falha ao baixar mídia msg {message.id}: {e}"
                            )

                    count += 1
                    progress.update(task, description=f"Baixando... ({count} mensagens)")

                # Flush do batch restante
                _flush_batch()

            return count

    console.print(f"[blue]💾 Iniciando backup de {entity_id}...[/]")

    try:
        total = run_async(_backup())
        console.print(
            f"[green]✓ Backup completo! {total} mensagens salvas em {output_path}[/]"
        )
    except RateLimitError as e:
        console.print(f"[yellow]⚠️ Rate limit: {e}[/]")
        console.print(f"[dim]Aguarde {e.wait_seconds}s e tente novamente[/]")
    except TelegramError as e:
        console.print(f"[red]Erro no backup: {e}[/]")
