#!/bin/bash
# Bootstrap script para desenvolvimento local

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Telegram GFCR - Setup${NC}"

# Verificar UV
if ! command -v uv &> /dev/null; then
    echo "UV não encontrado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null
fi

# Sincronizar dependências
echo -e "${GREEN}📦 Sincronizando dependências...${NC}"
uv sync

# Copiar .env se não existir
if [ ! -f .env ]; then
    echo -e "${GREEN}📝 Criando .env a partir do template...${NC}"
    cp .env.example .env
    echo "⚠️  Configure suas credenciais em .env antes de usar!"
fi

# Executar CLI
echo -e "${GREEN}✅ Setup completo!${NC}"
echo ""
echo "Para iniciar:"
echo "  uv run telegram-gfcr --help"
echo "  uv run telegram-gfcr interactive"
