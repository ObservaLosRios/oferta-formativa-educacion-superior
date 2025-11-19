"""Command line interface for running the ETL pipeline."""

from __future__ import annotations

from pathlib import Path

import typer

from .config.loader import ConfigLoader
from .pipeline import ETLPipeline
from .extractors.base import CSVExtractor
from .transformers.offer_transformer import OfferTransformer
from .loaders.dataframe_loader import DataFrameWriter


def run(config: Path = typer.Option("config/settings.yaml", exists=True, help="Path to the ETL YAML configuration.")) -> None:
    settings = ConfigLoader(config_path=config).load()
    extractor = CSVExtractor(settings.paths.raw_offers)
    transformer = OfferTransformer(settings)
    writer = DataFrameWriter(
        processed_dir=settings.paths.processed_dir,
        docs_dir=settings.paths.docs_dir,
    )
    pipeline = ETLPipeline(extractor, transformer, writer, settings)
    result = pipeline.run()
    typer.echo(
        f"ETL finished: {result.row_count} registros limpios -> {result.clean_output_path}\n"
        f"Resumen agregado publicado en {result.summary_output_path}"
    )


def main() -> None:
    typer.run(run)


if __name__ == "__main__":
    main()
