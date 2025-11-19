"""Configuration models for the Oferta Formativa ETL pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class ProjectMetadata:
    """Basic project information used in logs and reporting."""

    name: str
    description: str


@dataclass
class PathConfig:
    """Holds project path configuration and ensures required directories exist."""

    raw_offers: Path
    processed_dir: Path
    docs_dir: Path

    def ensure_directories(self) -> None:
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class EtlConfig:
    clean_output: str
    summary_output: str
    months_per_year: int
    filter_vigencia: str


@dataclass(frozen=True)
class CurrencyConfig:
    default_format: str
    uf_to_clp: float


@dataclass(frozen=True)
class ColumnConfig:
    keep: List[str]
    rename_map: Dict[str, str]
    integer: List[str]
    currency: List[str]


@dataclass(frozen=True)
class ReportConfig:
    summary_group_keys: List[str]


@dataclass
class Settings:
    project: ProjectMetadata
    paths: PathConfig
    etl: EtlConfig
    currency: CurrencyConfig
    columns: ColumnConfig
    report: ReportConfig

    def prepare_environment(self) -> None:
        """Create directories declared in the configuration."""

        self.paths.ensure_directories()
