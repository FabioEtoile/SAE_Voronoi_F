"""Résultat unifié d'un calcul de diagramme de Voronoi."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from voronoi.core.geometry import Point, Edge


@dataclass
class VoronoiDiagram:
    """Résultat d'un calcul Voronoi, produit par n'importe quel algorithme."""

    sites: list[Point]
    edges: list[Edge] = field(default_factory=list)
    vertices: list[Point] = field(default_factory=list)
    regions: dict[int, list[Point]] = field(default_factory=dict)
    pixel_assignments: Optional[list[list[int]]] = None
    width: int = 0
    height: int = 0
