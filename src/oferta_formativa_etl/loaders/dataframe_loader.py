"""Loaders that persist pandas DataFrames to the filesystem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class DataFrameWriter:
    """Persists transformed artefacts respecting SRP."""

    processed_dir: Path
    docs_dir: Path

    def save_clean(self, frame: pd.DataFrame, filename: str) -> Path:
        target = self.processed_dir / filename
        self._write(frame, target)
        return target

    def save_summary(self, frame: pd.DataFrame, filename: str) -> Path:
        target = self.docs_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".csv":
            frame.to_csv(target, index=False)
        else:
            self._write(frame, target)
        return target

    def _write(self, frame: pd.DataFrame, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".parquet":
            frame.to_parquet(path, index=False)
        else:
            frame.to_csv(path, index=False)
