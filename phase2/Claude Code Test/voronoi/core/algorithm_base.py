"""Classe abstraite pour les algorithmes de Voronoi (Strategy pattern)."""

from abc import ABC, abstractmethod

from voronoi.core.geometry import Point, BoundingBox
from voronoi.core.voronoi_result import VoronoiDiagram


class VoronoiAlgorithm(ABC):
    """Interface commune pour tous les algorithmes de Voronoi."""

    @abstractmethod
    def compute(self, sites: list[Point], bbox: BoundingBox) -> VoronoiDiagram:
        """Calcule le diagramme de Voronoi pour les sites donnés dans la bbox."""
        ...
