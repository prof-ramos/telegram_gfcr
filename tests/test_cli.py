"""Testes do CLI principal."""

from typer.testing import CliRunner

from telegram_gfcr.cli import app

runner = CliRunner()


def test_help() -> None:
    """Testa comando --help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "telegram-gfcr" in result.stdout


def test_version() -> None:
    """Testa comando --version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_list_help() -> None:
    """Testa help do comando list."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "Lista grupos" in result.stdout


def test_backup_help() -> None:
    """Testa help do comando backup."""
    result = runner.invoke(app, ["backup", "--help"])
    assert result.exit_code == 0
    assert "Faz backup" in result.stdout
