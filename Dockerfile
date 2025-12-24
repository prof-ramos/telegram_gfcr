# Build stage
FROM python:3.12-alpine AS builder

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar apenas arquivos de dependência primeiro (cache)
COPY pyproject.toml ./

# Instalar dependências no sistema
RUN uv pip install --system .

# Production stage
FROM python:3.12-alpine

WORKDIR /app

# Copiar dependências instaladas
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fonte
COPY src/ ./src/

# Criar diretório de config
RUN mkdir -p /root/.config/telegram-gfcr

# Volume para persistir sessão
VOLUME ["/root/.config/telegram-gfcr"]

# Entry point
ENTRYPOINT ["python", "-m", "telegram_gfcr.cli"]
CMD ["--help"]
