"""Configuração via Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas via variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TELEGRAM_",
        env_file_encoding="utf-8",
    )

    # Telegram API
    api_id: int
    api_hash: str
    phone: str

    # Session
    session_name: str = "telegram_gfcr"

    # Paths
    data_dir: Path = Path.home() / ".config" / "telegram-gfcr"

    # Debug
    debug: bool = False

    def ensure_data_dir(self) -> Path:
        """Cria diretório de dados se não existir."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir

    @property
    def session_path(self) -> Path:
        """Caminho completo do arquivo de sessão com permissões restritas."""
        path = self.ensure_data_dir() / self.session_name
        # Proteger arquivo de sessão com permissões 0600 (apenas owner lê/escreve)
        session_file = path.with_suffix(".session")
        if session_file.exists():
            session_file.chmod(0o600)
        return path


def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()  # type: ignore[call-arg]
