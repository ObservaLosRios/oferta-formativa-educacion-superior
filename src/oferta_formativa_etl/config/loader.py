"""Utilities to load YAML configuration into strongly-typed settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .models import (
    ColumnConfig,
    CurrencyConfig,
    EtlConfig,
    PathConfig,
    ProjectMetadata,
    ReportConfig,
    Settings,
)


class ConfigLoader:
    """Loads configuration files with minimal responsibilities (SRP)."""

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    def load(self) -> Settings:
        raw_cfg = self._read_yaml(self._config_path)
        settings = Settings(
            project=ProjectMetadata(**raw_cfg["project"]),
            paths=PathConfig(**self._resolve_paths(raw_cfg["paths"])),
            etl=EtlConfig(**raw_cfg["etl"]),
            currency=CurrencyConfig(**raw_cfg["currency"]),
            columns=ColumnConfig(**raw_cfg["columns"]),
            report=ReportConfig(**raw_cfg["report"]),
        )
        settings.prepare_environment()
        return settings

    def _resolve_paths(self, raw_paths: Dict[str, str]) -> Dict[str, Path]:
        base_dir = self._config_path.parent.parent
        resolved = {
            key: (base_dir / Path(value)).resolve()
            for key, value in raw_paths.items()
        }
        return resolved

    @staticmethod
    def _read_yaml(path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
