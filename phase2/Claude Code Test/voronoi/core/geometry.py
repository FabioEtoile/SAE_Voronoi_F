"""Primitives géométriques pour le diagramme de Voronoi."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Point:
    """Point 2D immutable."""

    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        """Distance euclidienne vers un autre point."""
        return math.sqrt(self.distance_sq(other))

    def distance_sq(self, other: Point) -> float:
        """Distance euclidienne au carré (évite le sqrt)."""
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass(frozen=True)
class Edge:
    """Segment de droite entre deux points."""

    start: Point
    end: Point

    def length(self) -> float:
        """Longueur du segment."""
        return self.start.distance_to(self.end)


@dataclass
class HalfEdge:
    """Demi-arête dirigée pour la structure DCEL."""

    origin: Optional[Point] = None
    twin: Optional[HalfEdge] = None
    left_site: Optional[Point] = None
    right_site: Optional[Point] = None
    _endpoint: Optional[Point] = None

    def finish(self, vertex: Point) -> None:
        """Définit le point terminal de cette demi-arête."""
        self._endpoint = vertex

    @property
    def endpoint(self) -> Optional[Point]:
        return self._endpoint

    def to_edge(self) -> Optional[Edge]:
        """Convertit en Edge si les deux extrémités sont définies."""
        if self.origin is not None and self._endpoint is not None:
            return Edge(self.origin, self._endpoint)
        return None


@dataclass
class BoundingBox:
    """Boîte englobante alignée sur les axes."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    def contains(self, p: Point) -> bool:
        """Vérifie si un point est dans la boîte."""
        return self.x_min <= p.x <= self.x_max and self.y_min <= p.y <= self.y_max

    def clip_segment(
        self, p1: Point, p2: Point
    ) -> Optional[tuple[Point, Point]]:
        """Clippe un segment aux limites de la boîte (Cohen-Sutherland)."""
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y

        INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

        def outcode(x: float, y: float) -> int:
            code = INSIDE
            if x < self.x_min:
                code |= LEFT
            elif x > self.x_max:
                code |= RIGHT
            if y < self.y_min:
                code |= BOTTOM
            elif y > self.y_max:
                code |= TOP
            return code

        code1 = outcode(x1, y1)
        code2 = outcode(x2, y2)

        for _ in range(20):
            if not (code1 | code2):
                return (Point(x1, y1), Point(x2, y2))
            if code1 & code2:
                return None

            code_out = code1 if code1 else code2
            dx = x2 - x1
            dy = y2 - y1

            if code_out & TOP:
                x = x1 + dx * (self.y_max - y1) / dy if dy != 0 else x1
                y = self.y_max
            elif code_out & BOTTOM:
                x = x1 + dx * (self.y_min - y1) / dy if dy != 0 else x1
                y = self.y_min
            elif code_out & RIGHT:
                y = y1 + dy * (self.x_max - x1) / dx if dx != 0 else y1
                x = self.x_max
            else:
                y = y1 + dy * (self.x_min - x1) / dx if dx != 0 else y1
                x = self.x_min

            if code_out == code1:
                x1, y1 = x, y
                code1 = outcode(x1, y1)
            else:
                x2, y2 = x, y
                code2 = outcode(x2, y2)

        return None
