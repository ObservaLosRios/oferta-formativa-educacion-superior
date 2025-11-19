"""Transformer interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Transformer(ABC):
    """All transformers must implement a transform method returning a DataFrame."""

    @abstractmethod
    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
