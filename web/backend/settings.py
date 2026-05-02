"""Configurare runtime pentru backend-ul web."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _csv_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if value is None:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BackendSettings:
    app_env: str
    host: str
    port: int
    reload: bool
    data_root: Path
    cors_origins: list[str]
    applicationinsights_connection_string: str | None

    @property
    def runs_root(self) -> Path:
        return (self.data_root / "runs").resolve()

    @property
    def environments_root(self) -> Path:
        return (self.data_root / "environments").resolve()

    @property
    def allow_cors_credentials(self) -> bool:
        return "*" not in self.cors_origins


def load_settings() -> BackendSettings:
    app_env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    return BackendSettings(
        app_env=app_env,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=_bool_env("RELOAD", app_env != "production"),
        data_root=Path(os.getenv("DATA_ROOT", "data")).resolve(),
        cors_origins=_csv_env("CORS_ORIGINS", ["*"]),
        applicationinsights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
    )


settings = load_settings()
