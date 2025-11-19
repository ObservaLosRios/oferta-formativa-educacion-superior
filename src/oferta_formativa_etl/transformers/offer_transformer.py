"""Domain-specific transformations for the oferta formativa dataset."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from ..config.models import Settings
from .base import Transformer


class OfferTransformer(Transformer):
    """Cleans, normalises and enriches Oferta Formativa records."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        prepared = frame.copy()
        prepared = self._select_columns(prepared)
        prepared = self._rename_columns(prepared)
        prepared = self._cast_integers(prepared)
        prepared = self._normalise_currency(prepared)
        prepared = self._clean_strings(prepared)
        prepared = self._derive_features(prepared)
        prepared = self._filter_vigencia(prepared)
        return prepared

    def _select_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame.loc[:, self._settings.columns.keep]

    def _rename_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame.rename(columns=self._settings.columns.rename_map)

    def _cast_integers(self, frame: pd.DataFrame) -> pd.DataFrame:
        for column in self._settings.columns.integer:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0).astype("Int64")
        return frame

    def _normalise_currency(self, frame: pd.DataFrame) -> pd.DataFrame:
        if "formato_valor" not in frame.columns:
            return frame
        uf_mask = frame["formato_valor"].str.contains("UF", case=False, na=False)
        pesos_mask = frame["formato_valor"].str.contains("peso", case=False, na=False)

        for column in self._settings.columns.currency:
            frame[column] = (
                pd.to_numeric(frame[column], errors="coerce")
                .fillna(0.0)
            )
            frame.loc[uf_mask, column] = (
                frame.loc[uf_mask, column] * self._settings.currency.uf_to_clp
            )
            frame.loc[:, column] = (
                frame[column].round(0).astype("Int64")
            )
        return frame

    def _clean_strings(self, frame: pd.DataFrame) -> pd.DataFrame:
        string_columns = frame.select_dtypes(include=["string", "object"]).columns
        for column in string_columns:
            frame[column] = frame[column].str.strip()
        return frame

    def _derive_features(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame["total_vacantes"] = (
            frame["vacantes_semestre_uno"].fillna(0)
            + frame["vacantes_semestre_dos"].fillna(0)
        )
        months = max(self._settings.etl.months_per_year, 1)
        frame["arancel_mensual_estimado"] = (
            frame["arancel_anual"].fillna(0) / months
        )
        frame["es_programa_vigente"] = frame["vigencia"].str.contains(
            "Vigente", case=False, na=False
        )
        frame["es_acreditado"] = frame["acreditacion"].str.contains(
            "Acreditada", case=False, na=False
        )
        frame["requiere_demre"] = frame["demre"].fillna(0) > 0
        return frame

    def _filter_vigencia(self, frame: pd.DataFrame) -> pd.DataFrame:
        vigencia = self._settings.etl.filter_vigencia
        mask = frame["vigencia"].str.contains(vigencia, case=False, na=False)
        return frame.loc[mask].reset_index(drop=True)

    @staticmethod
    def enforce_column_order(
        frame: pd.DataFrame, columns: Iterable[str]
    ) -> pd.DataFrame:
        present = [column for column in columns if column in frame.columns]
        remainder = [column for column in frame.columns if column not in present]
        return frame[present + remainder]
