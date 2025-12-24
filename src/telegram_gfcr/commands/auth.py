"""Comando de autenticação."""

from rich.console import Console

from ..core.client import TelegramClientWrapper, run_async
from ..core.errors import AuthenticationError, TelegramError

console = Console()


def run_auth(phone: str) -> None:
    """Executa autenticação no Telegram."""
    console.print(f"[blue]🔐 Autenticando {phone}...[/]")

    async def _auth() -> bool:
        wrapper = TelegramClientWrapper()
        try:
            return await wrapper.authenticate(phone)
        finally:
            await wrapper.disconnect()

    try:
        success = run_async(_auth())
        if success:
            console.print("[green]✓ Sessão salva com sucesso![/]")
    except AuthenticationError as e:
        console.print(f"[red]✗ {e}[/]")
    except TelegramError as e:
        console.print(f"[red]✗ Erro: {e}[/]")
