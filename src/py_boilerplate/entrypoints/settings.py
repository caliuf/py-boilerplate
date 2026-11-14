"""Configurazione runtime validata all'avvio di ogni processo.

Una sola configurazione tipizzata per processo, caricata nel composition root:
i moduli di libreria non leggono l'environment in autonomia.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from py_boilerplate.contracts.logging import LogLevel

type AppEnv = Literal["development", "test", "production"]


class RuntimeSettings(BaseSettings):
    """Variabili comuni a CLI, API e MCP."""

    model_config = SettingsConfigDict(extra="ignore", case_sensitive=False)

    log_level: LogLevel = "info"
    app_env: AppEnv = "production"

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: object) -> object:
        """Accetta `LOG_LEVEL=INFO` oltre alla forma minuscola canonica."""

        return value.lower() if isinstance(value, str) else value

    @property
    def json_logs(self) -> bool:
        """Log JSON fuori dallo sviluppo locale; console pretty in sviluppo."""

        return self.app_env != "development"


class ApiSettings(RuntimeSettings):
    """Variabili specifiche del deployable HTTP."""

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8100, ge=1, le=65535)
