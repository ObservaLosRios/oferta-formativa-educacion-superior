"""Extractor interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class Extractor(ABC):
    """Abstract extractor to enforce a consistent contract across data sources."""

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        raise NotImplementedError


class CSVExtractor(Extractor):
    """Concrete extractor for CSV files."""

    def __init__(self, file_path: Path, dtype_backend: str = "pyarrow") -> None:
        self._file_path = file_path
        self._dtype_backend = dtype_backend

    def extract(self) -> pd.DataFrame:
        if not self._file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._file_path}")
        return pd.read_csv(
            self._file_path,
            dtype_backend=self._dtype_backend,
            low_memory=False,
        )
