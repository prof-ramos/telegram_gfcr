"""Exceções customizadas e decorators para error handling do Telethon."""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from loguru import logger
from rich.console import Console
from telethon import errors

console = Console()
T = TypeVar("T")


# ========== EXCEÇÕES CUSTOMIZADAS ==========


class TelegramError(Exception):
    """Base para erros customizados."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class AuthenticationError(TelegramError):
    """Erro de autenticação (credenciais, código, 2FA)."""

    pass


class TelegramPermissionError(TelegramError):
    """Erro de permissões (admin required, banned, etc)."""

    pass


class RateLimitError(TelegramError):
    """Erro de rate limit (FloodWait, SlowMode)."""

    def __init__(self, message: str, wait_seconds: int, original_error: Exception | None = None):
        super().__init__(message, original_error)
        self.wait_seconds = wait_seconds


# ========== DECORATORS ==========


def handle_telethon_errors(operation_name: str) -> Callable:
    """
    Decorator que converte exceções do Telethon em exceções customizadas.

    Usage:
        @handle_telethon_errors("authenticate")
        async def authenticate(self, phone: str) -> bool:
            await self.client.sign_in(phone, code)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)

            # ===== AUTENTICAÇÃO =====
            except errors.PhoneCodeInvalidError as e:
                logger.error(f"{operation_name}: Código inválido")
                raise AuthenticationError(
                    "Código de autenticação inválido.", original_error=e
                ) from e

            except errors.PhoneCodeExpiredError as e:
                logger.error(f"{operation_name}: Código expirado")
                raise AuthenticationError(
                    "Código expirado. Solicite um novo.", original_error=e
                ) from e

            except errors.SessionPasswordNeededError as e:
                logger.error(f"{operation_name}: 2FA habilitado")
                raise AuthenticationError(
                    "2FA habilitado. Não suportado ainda.", original_error=e
                ) from e

            except errors.PhoneNumberInvalidError as e:
                logger.error(f"{operation_name}: Número inválido")
                raise AuthenticationError("Número de telefone inválido.", original_error=e) from e

            except errors.AuthKeyUnregisteredError as e:
                logger.error(f"{operation_name}: Sessão não autorizada")
                raise AuthenticationError(
                    "Sessão expirada. Execute 'telegram-gfcr auth <phone>'.", original_error=e
                ) from e

            # ===== RATE LIMITING =====
            except errors.FloodWaitError as e:
                wait_time = e.seconds
                logger.warning(f"{operation_name}: FloodWait de {wait_time}s")
                raise RateLimitError(
                    f"Rate limit atingido. Aguarde {wait_time} segundos.",
                    wait_seconds=wait_time,
                    original_error=e,
                ) from e

            except errors.SlowModeWaitError as e:
                wait_time = e.seconds
                logger.warning(f"{operation_name}: SlowMode {wait_time}s")
                raise RateLimitError(
                    f"Modo lento ativo. Aguarde {wait_time} segundos.",
                    wait_seconds=wait_time,
                    original_error=e,
                ) from e

            # ===== PERMISSÕES =====
            except errors.ChatAdminRequiredError as e:
                logger.error(f"{operation_name}: Admin required")
                raise TelegramPermissionError(
                    "Você precisa ser admin para executar esta operação.", original_error=e
                ) from e

            except errors.ChannelPrivateError as e:
                logger.error(f"{operation_name}: Canal privado")
                raise TelegramPermissionError(
                    "Canal privado ou você não tem acesso.", original_error=e
                ) from e

            except errors.UserBannedInChannelError as e:
                logger.error(f"{operation_name}: Usuário banido")
                raise TelegramPermissionError(
                    "Você está banido deste canal.", original_error=e
                ) from e

            except errors.ChatWriteForbiddenError as e:
                logger.error(f"{operation_name}: Escrita proibida")
                raise TelegramPermissionError(
                    "Sem permissão para escrever neste chat.", original_error=e
                ) from e

            # ===== ENTIDADES/MENSAGENS =====
            except errors.PeerIdInvalidError as e:
                logger.error(f"{operation_name}: ID inválido")
                raise TelegramError("ID inválido. Verifique o número.", original_error=e) from e

            except errors.MessageIdInvalidError as e:
                logger.warning(f"{operation_name}: Mensagem inválida")
                raise TelegramError("Mensagem não pode ser processada.", original_error=e) from e

            # ===== MÍDIA =====
            except errors.FileReferenceExpiredError as e:
                logger.warning(f"{operation_name}: Referência expirada")
                raise TelegramError("Referência de arquivo expirada.", original_error=e) from e

            # ===== GENÉRICO RPC =====
            except errors.RPCError as e:
                logger.error(f"{operation_name}: RPC error: {e}")
                raise TelegramError(f"Erro do Telegram: {e}", original_error=e) from e

            # ===== FALLBACK =====
            except Exception as e:
                logger.exception(f"{operation_name}: Erro inesperado")
                raise TelegramError(f"Erro inesperado: {e}", original_error=e) from e

        return wrapper  # type: ignore[return-value]

    return decorator


def retry_on_flood(max_retries: int = 3, base_delay: float = 1.0) -> Callable:
    """
    Decorator para retry automático em FloodWaitError com backoff exponencial.

    Args:
        max_retries: Número máximo de tentativas
        base_delay: Delay base para backoff (dobra a cada retry)

    Usage:
        @retry_on_flood(max_retries=3)
        @handle_telethon_errors("download_media")
        async def download_media(message, path):
            await message.download_media(file=path)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            retries = 0

            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)

                except errors.FloodWaitError as e:
                    wait_time = e.seconds
                    retries += 1

                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) atingido para FloodWait")
                        raise RateLimitError(
                            f"Rate limit persistente após {max_retries} tentativas.",
                            wait_seconds=wait_time,
                            original_error=e,
                        ) from e

                    # Backoff exponencial: base_delay * 2^(retries-1)
                    backoff = base_delay * (2 ** (retries - 1))
                    actual_wait = max(wait_time, backoff)

                    logger.warning(
                        f"FloodWait {wait_time}s. Retry {retries}/{max_retries} em {actual_wait}s"
                    )
                    console.print(
                        f"[yellow]⏳ Rate limit. Aguardando {actual_wait:.0f}s... "
                        f"(tentativa {retries}/{max_retries})[/]"
                    )

                    await asyncio.sleep(actual_wait)

            raise RuntimeError("Retry loop terminou sem retornar")

        return wrapper  # type: ignore[return-value]

    return decorator
