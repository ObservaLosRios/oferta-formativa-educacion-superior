"""Unit tests for the OfferTransformer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from oferta_formativa_etl.config.models import (
    ColumnConfig,
    CurrencyConfig,
    EtlConfig,
    PathConfig,
    ProjectMetadata,
    ReportConfig,
    Settings,
)
from oferta_formativa_etl.transformers.offer_transformer import OfferTransformer


def _build_settings(tmp_path: Path) -> Settings:
    path_config = PathConfig(
        raw_offers=tmp_path / "raw.csv",
        processed_dir=tmp_path / "processed",
        docs_dir=tmp_path / "docs",
    )
    settings = Settings(
        project=ProjectMetadata(name="test", description="test"),
        paths=path_config,
        etl=EtlConfig(
            clean_output="clean.parquet",
            summary_output="summary.csv",
            months_per_year=12,
            filter_vigencia="Vigente con estudiantes nuevos",
        ),
        currency=CurrencyConfig(default_format="Monto en Pesos", uf_to_clp=37000),
        columns=ColumnConfig(
            keep=[
                "Año",
                "Código Único",
                "Nombre IES",
                "Nombre Carrera",
                "Vigencia",
                "Formato Valor",
                "Matrícula Anual",
                "Arancel Anual",
                "Vacantes Semestre Uno",
                "Vacantes Semestre Dos",
                "Acreditación Carrera o Programa",
                "Demre",
                "Área del conocimiento",
                "Región Sede",
            ],
            rename_map={
                "Año": "anio",
                "Código Único": "codigo_unico",
                "Nombre IES": "nombre_ies",
                "Nombre Carrera": "nombre_carrera",
                "Vigencia": "vigencia",
                "Formato Valor": "formato_valor",
                "Matrícula Anual": "matricula_anual",
                "Arancel Anual": "arancel_anual",
                "Vacantes Semestre Uno": "vacantes_semestre_uno",
                "Vacantes Semestre Dos": "vacantes_semestre_dos",
                "Acreditación Carrera o Programa": "acreditacion",
                "Demre": "demre",
                "Área del conocimiento": "area_conocimiento",
                "Región Sede": "region_sede",
            },
            integer=["vacantes_semestre_uno", "vacantes_semestre_dos", "anio"],
            currency=["matricula_anual", "arancel_anual"],
        ),
        report=ReportConfig(summary_group_keys=["region_sede", "area_conocimiento"]),
    )
    settings.prepare_environment()
    return settings


def test_transformer_filters_and_aggregates(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    transformer = OfferTransformer(settings)
    df = pd.DataFrame(
        {
            "Año": [2025, 2025, 2025],
            "Código Único": ["A", "B", "C"],
            "Nombre IES": ["IES 1", "IES 2", "IES 3"],
            "Nombre Carrera": ["Enfermería", "Odontología", "Medicina"],
            "Vigencia": [
                "Vigente con estudiantes nuevos",
                "Vigente con estudiantes nuevos",
                "Vigente sin estudiantes nuevos",
            ],
            "Formato Valor": ["Monto en Pesos", "Monto en UF", "Monto en Pesos"],
            "Matrícula Anual": [200000, 10, 100000],
            "Arancel Anual": [1000000, 50, 900000],
            "Vacantes Semestre Uno": [40, 20, 15],
            "Vacantes Semestre Dos": [10, 10, 5],
            "Acreditación Carrera o Programa": [
                "Acreditada",
                "No Acreditada",
                "Acreditada",
            ],
            "Demre": [1, 0, 0],
            "Área del conocimiento": ["Salud", "Salud", "Salud"],
            "Región Sede": ["Biobío", "Biobío", "Biobío"],
        }
    )

    result = transformer.transform(df)

    # drops the non-vigente row
    assert len(result) == 2
    assert set(result["codigo_unico"]) == {"A", "B"}

    # currency conversion for UF
    uf_row = result[result["codigo_unico"] == "B"].iloc[0]
    assert uf_row["arancel_anual"] == 50 * 37000

    # derived metrics
    first_row = result[result["codigo_unico"] == "A"].iloc[0]
    assert first_row["total_vacantes"] == 50
    assert first_row["arancel_mensual_estimado"] == 1000000 / 12
    assert bool(first_row["es_acreditado"]) is True
    assert bool(first_row["requiere_demre"]) is True
