"""Genera el dataset vial local desde OpenStreetMap.

Uso desde la raíz del repositorio:

    python scripts/generate_graph.py
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

import osmnx as ox


REPOSITORY_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "app"
    / "data"
    / "graph"
    / "miraflores_san_isidro.graphml"
)
PLACES = (
    "Miraflores, Lima, Peru",
    "San Isidro, Lima, Peru",
)
MINIMUM_NODES = 1_500


def generate_graph(output: Path, overwrite: bool = False) -> None:
    """Descarga, valida y guarda atómicamente la red vial para conducir."""

    if output.exists() and output.stat().st_size > 0 and not overwrite:
        raise FileExistsError(
            f"El dataset ya existe: {output}. Usa --overwrite para reemplazarlo."
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    graph = ox.graph.graph_from_place(
        list(PLACES),
        network_type="drive",
        simplify=True,
        retain_all=False,
    )

    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    if node_count < MINIMUM_NODES:
        raise ValueError(
            f"El grafo descargado tiene {node_count} nodos; "
            f"se requieren al menos {MINIMUM_NODES}."
        )
    if edge_count == 0:
        raise ValueError("El grafo descargado no contiene aristas.")

    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(
            dir=output.parent,
            prefix="graph_",
            suffix=".graphml",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

        ox.io.save_graphml(graph, filepath=temporary_path)
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    metadata = {
        "source": "OpenStreetMap",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "places": list(PLACES),
        "network_type": "drive",
        "simplified": True,
        "nodes": node_count,
        "edges": edge_count,
        "osmnx_version": ox.__version__,
    }
    metadata_path = output.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Dataset guardado en: {output}")
    print(f"Nodos: {node_count}")
    print(f"Aristas: {edge_count}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el grafo vial de Miraflores y San Isidro."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ruta de salida del archivo GraphML.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Reemplaza un dataset no vacío existente.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    generate_graph(arguments.output.resolve(), arguments.overwrite)
