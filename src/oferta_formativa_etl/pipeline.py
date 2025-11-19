"""High-level orchestration of the Oferta Formativa ETL."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config.models import Settings
from .extractors.base import Extractor
from .loaders.dataframe_loader import DataFrameWriter
from .transformers.offer_transformer import OfferTransformer


@dataclass(frozen=True)
class PipelineResult:
    clean_output_path: str
    summary_output_path: str
    row_count: int


class ETLPipeline:
    """Coordinates extract, transform and load steps."""

    def __init__(
        self,
        extractor: Extractor,
        transformer: OfferTransformer,
        writer: DataFrameWriter,
        settings: Settings,
    ) -> None:
        self._extractor = extractor
        self._transformer = transformer
        self._writer = writer
        self._settings = settings

    def run(self) -> PipelineResult:
        raw_frame = self._extractor.extract()
        clean_frame = self._transformer.transform(raw_frame)
        ordered_frame = OfferTransformer.enforce_column_order(
            clean_frame,
            columns=list(self._settings.columns.rename_map.values()),
        )
        clean_path = self._writer.save_clean(
            ordered_frame, self._settings.etl.clean_output
        )
        summary_frame = self._build_summary(ordered_frame)
        summary_path = self._writer.save_summary(
            summary_frame, self._settings.etl.summary_output
        )
        return PipelineResult(
            clean_output_path=str(clean_path),
            summary_output_path=str(summary_path),
            row_count=len(ordered_frame),
        )

    def _build_summary(self, frame: pd.DataFrame) -> pd.DataFrame:
        group_keys = self._settings.report.summary_group_keys
        missing = [key for key in group_keys if key not in frame.columns]
        if missing:
            raise KeyError(f"Missing summary columns: {missing}")
        summary = (
            frame.groupby(group_keys, dropna=False)
            .agg(
                program_count=("codigo_carrera", "nunique"),
                instituciones_distintas=("nombre_ies", "nunique"),
                vacantes_totales=("total_vacantes", "sum"),
                arancel_promedio=("arancel_anual", "mean"),
                matricula_promedio=("matricula_anual", "mean"),
            )
            .reset_index()
        )
        return summary.sort_values(by=["vacantes_totales"], ascending=False)
