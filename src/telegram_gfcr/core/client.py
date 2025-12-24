"""Wrapper assíncrono para Telethon."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable
from contextlib import asynccontextmanager

from loguru import logger
from rich.console import Console
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User

from ..config import get_settings
from .errors import handle_telethon_errors

console = Console()

# Singleton global do pool
_client_pool: TelegramClientPool | None = None
_pool_lock = asyncio.Lock()


class TelegramClientPool:
    """Pool singleton thread-safe para gerenciar conexão Telegram."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._wrapper: TelegramClientWrapper | None = None
        self._connection_lock = asyncio.Lock()
        self._connected = False
        self._ref_count = 0
        logger.info("TelegramClientPool criado")

    async def get_wrapper(self) -> TelegramClientWrapper:
        """Obtém wrapper conectado (cria se necessário)."""
        async with self._connection_lock:
            if self._wrapper is None:
                logger.info("Criando novo TelegramClientWrapper")
                self._wrapper = TelegramClientWrapper()

            if not self._connected:
                logger.info("Conectando cliente Telegram")
                await self._wrapper.connect()
                self._connected = True

            self._ref_count += 1
            logger.debug(f"Wrapper obtido. Refs ativas: {self._ref_count}")
            return self._wrapper

    async def release_wrapper(self) -> None:
        """Libera referência ao wrapper."""
        async with self._connection_lock:
            self._ref_count = max(0, self._ref_count - 1)
            logger.debug(f"Wrapper liberado. Refs ativas: {self._ref_count}")
            # Não desconecta automaticamente - mantém conexão viva

    async def disconnect(self) -> None:
        """Desconecta pool (usar apenas em shutdown)."""
        async with self._connection_lock:
            if self._wrapper and self._connected:
                logger.info("Desconectando pool")
                await self._wrapper.disconnect()
                self._connected = False
                self._ref_count = 0


async def get_pool() -> TelegramClientPool:
    """Obtém instância singleton do pool."""
    global _client_pool

    if _client_pool is None:
        async with _pool_lock:
            # Double-check locking
            if _client_pool is None:
                _client_pool = TelegramClientPool()

    return _client_pool


class TelegramClientWrapper:
    """Wrapper para gerenciar cliente Telethon."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: TelegramClient | None = None

    @property
    def client(self) -> TelegramClient:
        """Retorna cliente inicializado."""
        if self._client is None:
            self._client = TelegramClient(
                str(self.settings.session_path),
                self.settings.api_id,
                self.settings.api_hash,
            )
        return self._client

    @handle_telethon_errors("connect")
    async def connect(self) -> bool:
        """Conecta ao Telegram."""
        await self.client.connect()
        is_authorized = await self.client.is_user_authorized()
        logger.info(f"Conectado. Autorizado: {is_authorized}")
        return is_authorized

    async def disconnect(self) -> None:
        """Desconecta do Telegram."""
        if self._client:
            await self._client.disconnect()

    @handle_telethon_errors("authenticate")
    async def authenticate(self, phone: str) -> bool:
        """Autentica usuário via código SMS."""
        await self.client.connect()

        if await self.client.is_user_authorized():
            console.print("[green]✓ Já autenticado![/]")
            return True

        await self.client.send_code_request(phone)
        logger.info(f"Código enviado para {phone}")
        code = console.input("[yellow]Digite o código recebido: [/]")

        await self.client.sign_in(phone, code)
        console.print("[green]✓ Autenticado com sucesso![/]")
        logger.info(f"Autenticado com sucesso: {phone}")
        return True

    async def get_dialogs(
        self, entity_type: str = "all"
    ) -> list[tuple[int, str, str, int]]:
        """
        Lista diálogos do usuário.

        Returns:
            Lista de tuplas (id, nome, tipo, count_mensagens)
        """
        dialogs = []
        async for dialog in self.client.iter_dialogs():
            entity = dialog.entity
            dtype = "unknown"

            if isinstance(entity, User):
                dtype = "user"
            elif isinstance(entity, Chat):
                dtype = "group"
            elif isinstance(entity, Channel):
                dtype = "channel" if entity.broadcast else "supergroup"

            if entity_type != "all" and dtype != entity_type:
                continue

            dialogs.append((
                dialog.id,
                dialog.name or "Sem nome",
                dtype,
                dialog.unread_count,
            ))

        return dialogs


@asynccontextmanager
async def get_client() -> AsyncGenerator[TelegramClientWrapper, None]:
    """
    Context manager para cliente Telegram.

    Agora usa pool singleton em vez de criar nova instância.
    Backward compatible com código existente.
    """
    pool = await get_pool()
    wrapper = await pool.get_wrapper()

    try:
        yield wrapper
    finally:
        await pool.release_wrapper()


async def shutdown_pool() -> None:
    """Desconecta pool (chamar ao sair do app)."""
    global _client_pool


    if _client_pool:
        logger.info("Shutdown do pool")
        await _client_pool.disconnect()
        _client_pool = None


def run_async[T](coro: Awaitable[T]) -> T:
    """Executa coroutine em contexto síncrono."""
    return asyncio.run(coro)
