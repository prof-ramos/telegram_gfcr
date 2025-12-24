"""Entry point do CLI com Typer."""

import typer
from rich.console import Console

from . import __version__
from .core.logging import setup_logging

# Configurar logging ao importar o módulo
setup_logging()

app = typer.Typer(
    name="telegram-gfcr",
    help="CLI interativo para gerenciamento do Telegram",
    add_completion=True,
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    """Exibe versão e sai."""
    if value:
        console.print(f"[bold blue]telegram-gfcr[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Exibe versão do CLI",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Telegram GFCR - CLI interativo para gerenciamento do Telegram."""
    pass


@app.command()
def interactive() -> None:
    """Inicia modo REPL interativo."""
    from .interactive import start_session

    start_session()


@app.command()
def auth(
    phone: str = typer.Argument(..., help="Número de telefone com código do país (+5511...)"),
) -> None:
    """Autentica conta Telegram."""
    from .commands.auth import run_auth

    run_auth(phone)


@app.command(name="list")
def list_entities(
    entity_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Tipo de entidade: all, groups, channels, users",
    ),
) -> None:
    """Lista grupos, conversas e canais."""
    from .commands.list import run_list

    run_list(entity_type)


@app.command()
def backup(
    entity_id: int = typer.Argument(..., help="ID da entidade para backup"),
    output: str = typer.Option(None, "--output", "-o", help="Diretório de saída"),
    media: bool = typer.Option(False, "--media", "-m", help="Incluir mídias"),
) -> None:
    """Faz backup de uma conversa ou grupo."""
    from .commands.backup import run_backup

    run_backup(entity_id, output, media)


@app.command()
def forward(
    source_id: int = typer.Argument(..., help="ID da entidade origem"),
    dest_id: int = typer.Argument(..., help="ID da entidade destino"),
    limit: int = typer.Option(100, "--limit", "-l", help="Limite de mensagens"),
) -> None:
    """Encaminha mensagens entre entidades."""
    from .commands.forward import run_forward

    run_forward(source_id, dest_id, limit)


@app.command()
def search(
    query: str = typer.Argument(..., help="Termo de busca"),
    entity_id: int = typer.Option(None, "--id", help="ID da entidade (opcional)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Limite de resultados"),
) -> None:
    """Busca mensagens por texto."""
    from .commands.search import run_search

    run_search(query, entity_id, limit)


@app.command()
def leave(
    entity_id: int = typer.Argument(..., help="ID do grupo para sair"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar sem prompt"),
) -> None:
    """Sai de um grupo."""
    from .commands.leave import run_leave

    run_leave(entity_id, confirm)


if __name__ == "__main__":
    app()
