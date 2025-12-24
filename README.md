# 📱 Telegram GFCR

**CLI Interativo para o Telegram** — Uma experiência de terminal inteligente inspirada no [Claude Code](https://docs.anthropic.com/en/docs/claude-code) e [Gemini CLI](https://github.com/google-gemini/gemini-cli), para gerenciar grupos, conversas e mídias do Telegram.

```text
┌─────────────────────────────────────────────────────────────────┐
│  🤖 Telegram GFCR v0.1.0                                        │
│  Digite um comando ou use linguagem natural...                  │
├─────────────────────────────────────────────────────────────────┤
│  > list                                                         │
│                                                                 │
│  📂 Encontrados 12 grupos:                                      │
│  ├── [1] Dev Brasil (1,234 mensagens)                           │
│  ├── [2] Python BR (892 mensagens)                              │
│  └── [3] ...                                                    │
│                                                                 │
│  > backup 123456 --media                                        │
│  ⏳ Baixando mensagens... ████████████░░░░░░░░ 60%              │
└─────────────────────────────────────────────────────────────────┘
```

---

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![UV](https://img.shields.io/badge/UV-Package_Manager-7C3AED?style=flat-square&logo=astral&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-API-0088CC?style=flat-square&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Funcionalidades

| Comando | Descrição |
|---------|-----------|
| `interactive` | Modo REPL com autocomplete e histórico |
| `auth` | Autentica conta Telegram via SMS |
| `list` | Lista grupos, conversas e canais |
| `backup` | Faz backup de conversas (JSON + mídias) |
| `forward` | Encaminha mensagens entre entidades |
| `leave` | Sai de um grupo rapidamente |

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.12+**
- **[UV](https://docs.astral.sh/uv/)** — Gerenciador de pacotes Python
- Credenciais API Telegram → [my.telegram.org/apps](https://my.telegram.org/apps)

### Setup Rápido

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/telegram_gfcr.git
cd telegram_gfcr

# Instale dependências
uv sync

# Configure credenciais
cp .env.example .env
# Edite .env com seu API_ID e API_HASH
```

---

## ⚙️ Configuração

Edite o arquivo `.env`:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890
TELEGRAM_PHONE=+5511999999999
```

---

## 📖 Uso

### Modo Interativo (Recomendado)

```bash
uv run telegram-gfcr interactive
```

```text
🤖 Telegram GFCR v0.1.0
Digite 'help' para ver comandos disponíveis

telegram> list
telegram> backup 123456 --media
telegram> exit
```

### Comandos Diretos

```bash
# Autenticar
uv run telegram-gfcr auth +5511999999999

# Listar entidades
uv run telegram-gfcr list --type groups

# Fazer backup
uv run telegram-gfcr backup 123456 --media

# Encaminhar mensagens
uv run telegram-gfcr forward 123 456 --limit 50

# Sair de grupo
uv run telegram-gfcr leave 789 --yes
```

---

## 🛠️ Stack

| Tecnologia | Propósito |
|------------|-----------|
| [UV](https://docs.astral.sh/uv/) | Gerenciamento de pacotes |
| [Typer](https://typer.tiangolo.com/) | Framework CLI |
| [Rich](https://rich.readthedocs.io/) | Output visual |
| [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) | REPL interativo |
| [Telethon](https://docs.telethon.dev/) | API Telegram |
| [Pydantic](https://docs.pydantic.dev/) | Configuração |

---

## 📁 Estrutura

```text
telegram_gfcr/
├── src/telegram_gfcr/
│   ├── cli.py           # Entry point Typer
│   ├── interactive.py   # REPL prompt_toolkit
│   ├── config.py        # Pydantic settings
│   ├── core/
│   │   └── client.py    # Wrapper Telethon
│   └── commands/        # auth, list, backup, forward, leave
├── tests/
├── pyproject.toml
├── Dockerfile
└── .env.example
```

---

## 🐳 Docker

```bash
# Build
docker build -t telegram-gfcr .

# Run interativo
docker run --rm -it \
  -e TELEGRAM_API_ID=123 \
  -e TELEGRAM_API_HASH=abc \
  -v ~/.config/telegram-gfcr:/root/.config/telegram-gfcr \
  telegram-gfcr interactive
```

---

## 🧪 Desenvolvimento

```bash
# Rodar testes
uv run pytest tests/ -v

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

---

## 📝 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

## ⚠️ Aviso Legal

Uso pessoal e educacional. Respeite os [Termos de Serviço do Telegram](https://telegram.org/tos).

---

**Desenvolvido com ❤️ por [GFCR](https://github.com/gfcr)**
