# 🚀 Melhorias Baseadas em Best Practices do Telethon

## 1. Connection Pool & Reuso de Cliente

### ⚠️ Problema Atual
```python
# Cria nova instância a cada comando (AUTH.PY)
wrapper = TelegramClientWrapper()
await wrapper.authenticate(phone)
await wrapper.disconnect()
```

**Impacto**: Reconnexões frequentes = lentidão, overhead, possíveis rate limits

### ✅ Solução: Singleton Pattern com Context Manager

```python
# client.py - Implementar padrão singleton thread-safe
class TelegramClientWrapper:
    _instance: TelegramClientWrapper | None = None
    _lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self):
        if not self._client:
            self._client = TelegramClient(...)
            await self._client.connect()
        return self

    async def __aexit__(self, *args):
        # Manter conexão aberta entre comandos
        pass
```

**Benefício**: Reutiliza conexão, reduz latência, economiza banda

---

## 2. Error Handling Específico do Telethon

### ⚠️ Problema Atual
```python
try:
    await self.client.sign_in(phone, code)
except Exception as e:  # Muito genérico!
    console.print(f"[red]Erro: {e}[/]")
```

### ✅ Solução: Tratar exceções específicas

```python
from telethon.errors import (
    PhoneNumberInvalidError,
    PhoneNumberUnoccupiedError,
    InvalidPhoneError,
    CodeExpiredError,
    InvalidCodeError,
    SessionExpiredError,
)

try:
    await self.client.sign_in(phone, code)
except InvalidPhoneError:
    console.print("[red]Número de telefone inválido[/]")
except CodeExpiredError:
    console.print("[red]Código expirado. Solicite um novo[/]")
except InvalidCodeError:
    console.print("[red]Código incorreto[/]")
except SessionExpiredError:
    await self.client.disconnect()
    raise
```

**Benefício**: UX melhorada, debugging mais fácil, tratamento apropriado

---

## 3. Rate Limiting & Throttling

### ⚠️ Problema Atual
```python
async for message in client.iter_messages(entity_id):
    # Sem controle de rate limit!
    await message.download_media(file=str(media_dir))
```

### ✅ Solução: Implementar backoff exponencial

```python
import asyncio
from typing import Any

async def iter_with_backoff(
    async_iter,
    delay: float = 0.1,
    max_retries: int = 3
):
    """Itera com retry automático em rate limits."""
    from telethon.errors import FloodWaitError

    async for item in async_iter:
        retries = 0
        while retries < max_retries:
            try:
                yield item
                break
            except FloodWaitError as e:
                wait_time = e.seconds + (2 ** retries)  # Backoff exponencial
                console.print(f"[yellow]⏳ Rate limited. Aguardando {wait_time}s...[/]")
                await asyncio.sleep(wait_time)
                retries += 1
```

**Uso**:
```python
async for message in iter_with_backoff(client.iter_messages(entity_id)):
    count += 1
```

**Benefício**: Evita banimentos temporários, respeita limites do Telegram

---

## 4. Logging Estruturado com Loguru

### ⚠️ Problema Atual
```python
from loguru import loguru  # Importado mas não usado efetivamente!
console.print(f"[red]Erro no backup: {e}[/]")  # Sem contexto
```

### ✅ Solução: Estruturar logs com context

```python
from loguru import logger

# config.py - Configurar loguru
def configure_logging(debug: bool = False):
    logger.remove()  # Remove handler padrão
    logger.add(
        "logs/telegram_gfcr.log",
        level="DEBUG" if debug else "INFO",
        rotation="1 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )
    logger.add(
        lambda msg: console.print(msg.rstrip()),
        level="INFO",
        colorize=True
    )

# client.py - Usar contexto nos logs
class TelegramClientWrapper:
    async def authenticate(self, phone: str) -> bool:
        logger.info(f"Iniciando autenticação para {phone}")
        try:
            await self.client.send_code_request(phone)
            logger.debug(f"Código enviado para {phone}")
            # ...
        except Exception as e:
            logger.error(f"Falha na autenticação: {e}", exc_info=True)
            return False
```

**Benefício**: Debugging facilitado, auditoria, troubleshooting em produção

---

## 5. Batch I/O & Performance do Backup

### ⚠️ Problema Atual
```python
async for message in client.iter_messages(entity_id):
    with open(messages_file, "a", encoding="utf-8") as f:
        f.write(message.to_json() + "\n")  # Abre/fecha arquivo para cada mensagem!
```

**Impacto**: ~1000 aberturas de arquivo por 1000 mensagens = LENTO

### ✅ Solução: Batch writes

```python
async def _backup() -> int:
    async with get_client() as client:
        count = 0
        batch_size = 100
        batch = []

        async for message in client.client.iter_messages(entity_id):
            batch.append(message.to_json())

            if len(batch) >= batch_size:
                # Escrever em batch
                with open(messages_file, "a", encoding="utf-8") as f:
                    f.write("\n".join(batch) + "\n")
                batch = []
                count += len(batch)
                progress.update(task, description=f"Backup... ({count} msgs)")

        # Escrever resto
        if batch:
            with open(messages_file, "a", encoding="utf-8") as f:
                f.write("\n".join(batch) + "\n")
            count += len(batch)

    return count
```

**Benefício**: 10x+ mais rápido para grandes backups, menos I/O stress

---

## 6. Session File Security

### ⚠️ Problema Atual
```python
# config.py - Session salva com permissões padrão
return self.ensure_data_dir() / self.session_name
```

Session contém credenciais! Permissões insuficientes.

### ✅ Solução: Proteger arquivo de sessão

```python
from pathlib import Path
import stat

@property
def session_path(self) -> Path:
    """Caminho com permissões restritas."""
    path = self.ensure_data_dir() / self.session_name

    # Criar com permissões 0600 (apenas owner lê/escreve)
    if not path.exists():
        path.touch(mode=0o600)
    else:
        path.chmod(0o600)

    return path
```

**Benefício**: Previne acesso de outros usuários à sessão autenticada

---

## 7. Melhorar Type Hints & Type Safety

### ⚠️ Problema Atual
```python
def run_async[T](coro: T) -> T:
    """Executa coroutine em contexto síncrono."""
    return asyncio.get_event_loop().run_until_complete(coro)  # type: ignore
```

### ✅ Solução: Type hints corretos

```python
from typing import Awaitable, TypeVar

T = TypeVar("T")

def run_async(coro: Awaitable[T]) -> T:
    """Executa coroutine em contexto síncrono."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Fora de async context
        return asyncio.run(coro)

    # Dentro de async context, não chamar run_until_complete
    raise RuntimeError("Não chame run_async de dentro de uma coroutine")
```

**Benefício**: MyPy strict mode passa, melhor IDE support

---

## 8. Otimizar iter_dialogs() com Filtering

### ⚠️ Problema Atual
```python
async for dialog in self.client.iter_dialogs():
    # Filtra em Python depois
    if entity_type != "all" and dtype != entity_type:
        continue
```

### ✅ Solução: Usar offset-limit eficientemente

```python
async def get_dialogs(self, entity_type: str = "all") -> list[tuple[int, str, str, int]]:
    """Lista diálogos com paginação eficiente."""
    dialogs = []
    offset_date = None
    offset_id = 0
    offset_peer = await self.client.get_input_entity(self.client.get_me())

    while True:
        chunk = await self.client.get_dialogs(
            offset_date=offset_date,
            offset_id=offset_id,
            offset_peer=offset_peer,
            limit=100,  # Fetch em chunks
        )

        if not chunk:
            break

        for dialog in chunk:
            entity = dialog.entity
            dtype = self._get_entity_type(entity)

            if entity_type != "all" and dtype != entity_type:
                continue

            dialogs.append((
                dialog.id,
                dialog.name or "Sem nome",
                dtype,
                dialog.unread_count,
            ))

        # Preparar próxima página
        if len(chunk) < 100:
            break

        offset_date = chunk[-1].date
        offset_id = chunk[-1].id

    return dialogs
```

**Benefício**: Menos memória, melhor para contas com muitos diálogos

---

## 9. Melhorar Async Event Loop Management

### ⚠️ Problema Atual
```python
# cli.py - Chamadas síncronas para async
def interactive() -> None:
    from .interactive import start_session
    start_session()  # Precisa de run_async internamente

# Isso funciona mas é frágil
```

### ✅ Solução: Usar typer com async support

```python
import asyncio
import typer

app = typer.Typer()

@app.command()
async def auth(phone: str = typer.Argument(...)) -> None:
    """Autentica conta Telegram."""
    from .commands.auth import run_auth_async
    await run_auth_async(phone)

# Adaptar commands/ para retornar coroutines
async def run_auth_async(phone: str) -> None:
    """Executa autenticação no Telegram."""
    wrapper = TelegramClientWrapper()
    try:
        success = await wrapper.authenticate(phone)
        if success:
            console.print("[green]✓ Sessão salva![/]")
        else:
            console.print("[red]✗ Falha na autenticação[/]")
    finally:
        await wrapper.disconnect()
```

**Benefício**: Melhor integração com async ecosystem, menos boilerplate

---

## 10. Adicionar Retry Logic para Operações Críticas

### ⚠️ Problema Atual
```python
async for message in client.iter_messages(entity_id):
    # Sem retry!
    await message.download_media(file=str(media_dir))
```

### ✅ Solução: Retry automático com exponential backoff

```python
async def retry_async(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry com exponential backoff."""
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Tentativa {attempt + 1} falhou. Aguardando {delay}s...",
                    extra={"exception": e}
                )
                await asyncio.sleep(delay)
                delay *= backoff
            else:
                logger.error(f"Falhou após {max_retries} tentativas", exc_info=True)

    raise last_exception

# Uso
async for message in client.iter_messages(entity_id):
    if message.media:
        await retry_async(
            lambda: message.download_media(file=str(media_dir)),
            max_retries=3
        )
```

**Benefício**: Resiliência a falhas transientes (conexão, rate limits)

---

## 📋 Checklist de Implementação

- [ ] 1. Implementar Connection Pool Singleton
- [ ] 2. Adicionar Error Handling específico do Telethon
- [ ] 3. Implementar Rate Limit Backoff
- [ ] 4. Estruturar Logging com Loguru
- [ ] 5. Otimizar Backup com Batch I/O
- [ ] 6. Proteger Session File (chmod 0600)
- [ ] 7. Melhorar Type Hints
- [ ] 8. Otimizar iter_dialogs com Paginação
- [ ] 9. Usar Typer com Async Support
- [ ] 10. Adicionar Retry Logic

---

## 📚 Referências do Telethon

- **Docs Oficiais**: https://docs.telethon.dev/
- **Error Handling**: https://docs.telethon.dev/en/latest/basic/errors.html
- **Session Storage**: https://docs.telethon.dev/en/latest/concepts/sessions.html
- **Performance Tips**: https://docs.telethon.dev/en/latest/basic/asyncio.html
- **FloodWait Handling**: https://docs.telethon.dev/en/latest/basic/errors.html#flood-wait-error

---

## 🎯 Próximos Passos

1. **Prioridade Alta**: Implementar Connection Pool (1) + Error Handling (2)
2. **Prioridade Média**: Rate Limiting (3) + Logging (4)
3. **Prioridade Baixa**: Otimizações de performance (5, 8)

**Estimado**: 2-3 horas para implementar todas as melhorias
