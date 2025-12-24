# 📱 Telegram GFCR

**CLI Interativo para o Telegram** — Uma experiência de terminal inteligente inspirada no [Claude Code](https://docs.anthropic.com/en/docs/claude-code) e [Gemini CLI](https://github.com/google-gemini/gemini-cli), mas focada em gerenciar seus grupos, conversas e mídias do Telegram.

```text
┌─────────────────────────────────────────────────────────────────┐
│  🤖 Telegram GFCR v0.1.0                                        │
│  Digite um comando ou use linguagem natural...                  │
├─────────────────────────────────────────────────────────────────┤
│  > liste meus grupos                                            │
│                                                                 │
│  📂 Encontrados 12 grupos:                                      │
│  ├── [1] Dev Brasil (1,234 mensagens)                           │
│  ├── [2] Python BR (892 mensagens)                              │
│  └── [3] ...                                                    │
│                                                                 │
│  > faça backup do grupo 1                                       │
│  ⏳ Baixando mensagens... ████████████░░░░░░░░ 60%              │
└─────────────────────────────────────────────────────────────────┘
```

---

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![UV](https://img.shields.io/badge/UV-Package_Manager-7C3AED?style=flat-square&logo=astral&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-API-0088CC?style=flat-square&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| � **Terminal Interativo** | Converse naturalmente — digite comandos ou pergunte em linguagem natural |
| �📋 **Listar Entidades** | Visualize grupos, conversas e canais com IDs para fácil referência |
| 💾 **Backup Completo** | Baixe conversas inteiras de forma organizada e cronológica |
| 📤 **Encaminhamento** | Encaminhe mensagens para outro grupo como backup secundário |
| 🚪 **Gestão Rápida** | Saia de múltiplos grupos com comandos simples |
| 📊 **Metadados Locais** | Armazene e consulte histórico via SQLite |

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.12+**
- **[UV](https://docs.astral.sh/uv/)** — Gerenciador de pacotes e ambientes Python ultrarrápido
- Credenciais da API Telegram → [Obter aqui](https://my.telegram.org/apps)

### Instalando o UV

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Ou via Homebrew
brew install uv
```

### Configurando o Projeto

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/telegram_gfcr.git
cd telegram_gfcr

# Sincronize dependências (cria venv automaticamente)
uv sync

# Ative o ambiente virtual
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

---

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999
```

> [!TIP]
> Na primeira execução, você autenticará sua conta via código SMS/Telegram.

---

## 📖 Uso

### Iniciando o Terminal Interativo

```bash
# Inicie o CLI interativo
uv run telegram-gfcr

# Ou, se o venv estiver ativo:
telegram-gfcr
```

### Dentro do Terminal

```text
> ajuda                          # Exibe comandos disponíveis
> listar grupos                  # Lista todos os grupos
> backup grupo 123456            # Faz backup do grupo pelo ID
> encaminhar 123 para 456        # Encaminha mensagens entre grupos
> sair do grupo 789              # Sai de um grupo específico
> /exit                          # Encerra o CLI
```

### Comandos Diretos (não-interativo)

```bash
uv run telegram-gfcr listar
uv run telegram-gfcr backup --id 123456
uv run telegram-gfcr sair --id 789
```

---

## 🛠️ Stack Tecnológica

| Tecnologia | Propósito |
|------------|-----------|
| [UV](https://docs.astral.sh/uv/) | Gerenciamento de pacotes e ambientes Python |
| [Telethon](https://docs.telethon.dev/) | Interação com a API do Telegram |
| [Rich](https://rich.readthedocs.io/) | Interface de terminal rica e colorida |
| [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) | Input interativo com autocomplete |
| [SQLite](https://www.sqlite.org/) | Armazenamento local de metadados |

---

## 📁 Estrutura do Projeto

```text
telegram_gfcr/
├── src/
│   └── telegram_gfcr/
│       ├── __init__.py
│       ├── main.py         # Entry point e REPL interativo
│       ├── commands.py     # Handlers de comandos
│       ├── client.py       # Wrapper Telethon
│       ├── database.py     # Operações SQLite
│       ├── ui.py           # Componentes Rich/Prompt Toolkit
│       └── utils.py        # Funções auxiliares
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⚠️ Aviso Legal

Este projeto é apenas para uso pessoal e educacional. Respeite os [Termos de Serviço do Telegram](https://telegram.org/tos) ao utilizar esta ferramenta. O uso indevido da API pode resultar em banimento da sua conta.

---

---

**Desenvolvido com ❤️ por [GFCR](https://github.com/gfcr)**
