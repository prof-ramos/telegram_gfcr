"""Configuração estruturada do Loguru."""

import sys

from loguru import logger

from ..config import get_settings


def setup_logging() -> None:
    """Configura loguru com rotação de arquivos e console."""
    settings = get_settings()
    log_dir = settings.ensure_data_dir() / "logs"
    log_dir.mkdir(exist_ok=True)

    # Remove handler padrão
    logger.remove()

    # Console output (apenas se debug=True)
    if settings.debug:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}:{function}</cyan> - <level>{message}</level>"
            ),
        )

    # File output (sempre)
    logger.add(
        log_dir / "telegram_gfcr_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Novo arquivo à meia-noite
        retention="7 days",  # Mantém últimos 7 dias
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("Logging configurado")
