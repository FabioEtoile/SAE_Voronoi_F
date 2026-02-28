"""Algorithme de Voronoi par force brute (nearest neighbor pixel-par-pixel)."""

from voronoi.core.algorithm_base import VoronoiAlgorithm
from voronoi.core.geometry import Point, BoundingBox, Edge
from voronoi.core.voronoi_result import VoronoiDiagram


class BruteForceVoronoi(VoronoiAlgorithm):
    """
    Calcul pixel-par-pixel : pour chaque pixel, trouver le site le plus proche.
    Les arêtes sont extraites là où des pixels voisins appartiennent à des régions différentes.
    """

    def compute(self, sites: list[Point], bbox: BoundingBox) -> VoronoiDiagram:
        """Calcule le diagramme en assignant chaque pixel à son site le plus proche."""
        if not sites:
            return VoronoiDiagram(
                sites=sites,
                width=int(bbox.width),
                height=int(bbox.height),
            )

        width = int(bbox.width)
        height = int(bbox.height)

        assignments = self._assign_pixels(sites, bbox, width, height)
        edge_pixels = self._extract_edge_pixels(assignments, width, height)

        edges: list[Edge] = []
        for px, py in edge_pixels:
            world_x = bbox.x_min + px
            world_y = bbox.y_min + py
            edges.append(Edge(Point(world_x, world_y), Point(world_x, world_y)))

        return VoronoiDiagram(
            sites=sites,
            edges=edges,
            pixel_assignments=assignments,
            width=width,
            height=height,
        )

    def _assign_pixels(
        self,
        sites: list[Point],
        bbox: BoundingBox,
        width: int,
        height: int,
    ) -> list[list[int]]:
        """Assigne chaque pixel au site le plus proche. Retourne grille 2D d'indices."""
        assignments: list[list[int]] = []

        sites_xy = [(s.x, s.y) for s in sites]

        for py in range(height):
            row: list[int] = []
            world_y = bbox.y_min + py
            for px in range(width):
                world_x = bbox.x_min + px
                min_dist_sq = float("inf")
                nearest = 0
                for i, (sx, sy) in enumerate(sites_xy):
                    d = (world_x - sx) ** 2 + (world_y - sy) ** 2
                    if d < min_dist_sq:
                        min_dist_sq = d
                        nearest = i
                row.append(nearest)
            assignments.append(row)

        return assignments

    def _extract_edge_pixels(
        self,
        assignments: list[list[int]],
        width: int,
        height: int,
    ) -> list[tuple[int, int]]:
        """Identifie les pixels sur les frontières entre régions."""
        edge_pixels: list[tuple[int, int]] = []

        for py in range(height):
            for px in range(width):
                current = assignments[py][px]
                if px + 1 < width and assignments[py][px + 1] != current:
                    edge_pixels.append((px, py))
                elif py + 1 < height and assignments[py + 1][px] != current:
                    edge_pixels.append((px, py))

        return edge_pixels
