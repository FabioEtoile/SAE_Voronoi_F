"""Algorithme de Fortune (sweep line) pour le diagramme de Voronoi."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Optional

from voronoi.core.algorithm_base import VoronoiAlgorithm
from voronoi.core.geometry import Point, Edge, BoundingBox
from voronoi.core.voronoi_result import VoronoiDiagram

EPS = 1e-9


@dataclass
class _HalfEdgeRecord:
    """Enregistrement d'une demi-arête tracée pendant le sweep."""

    left_site: Point
    right_site: Point
    start: Optional[Point] = None
    end: Optional[Point] = None
    direction: tuple[float, float] = (0.0, 0.0)

    def finish(self, point: Point) -> None:
        self.end = point


class _Arc:
    """Arc parabolique dans la beachline."""

    __slots__ = ("site", "circle_event", "left_edge", "right_edge")

    def __init__(self, site: Point) -> None:
        self.site = site
        self.circle_event: Optional[_Event] = None
        self.left_edge: Optional[_HalfEdgeRecord] = None
        self.right_edge: Optional[_HalfEdgeRecord] = None


class _Event:
    """Événement dans la file de priorité."""

    __slots__ = ("y", "is_site", "point", "arc", "valid", "_counter")
    _global_counter: int = 0

    def __init__(
        self,
        y: float,
        is_site: bool,
        point: Point,
        arc: Optional[_Arc] = None,
    ) -> None:
        self.y = y
        self.is_site = is_site
        self.point = point
        self.arc = arc
        self.valid = True
        _Event._global_counter += 1
        self._counter = _Event._global_counter

    def __lt__(self, other: _Event) -> bool:
        if abs(self.y - other.y) < EPS:
            if self.is_site != other.is_site:
                return self.is_site
            return self._counter < other._counter
        return self.y < other.y


class FortuneVoronoi(VoronoiAlgorithm):
    """Algorithme de Fortune pour le calcul géométrique du diagramme de Voronoi."""

    def __init__(self) -> None:
        self._events: list[_Event] = []
        self._arcs: list[_Arc] = []
        self._edges: list[_HalfEdgeRecord] = []
        self._vertices: list[Point] = []

    def compute(self, sites: list[Point], bbox: BoundingBox) -> VoronoiDiagram:
        """Calcule le diagramme de Voronoi via l'algorithme de Fortune."""
        if len(sites) < 2:
            return VoronoiDiagram(sites=sites)

        self._events = []
        self._arcs = []
        self._edges = []
        self._vertices = []
        _Event._global_counter = 0

        sorted_sites = sorted(sites, key=lambda p: (p.y, p.x))
        unique_sites: list[Point] = [sorted_sites[0]]
        for s in sorted_sites[1:]:
            if abs(s.x - unique_sites[-1].x) > EPS or abs(s.y - unique_sites[-1].y) > EPS:
                unique_sites.append(s)

        if len(unique_sites) < 2:
            return VoronoiDiagram(sites=sites)

        for site in unique_sites:
            evt = _Event(site.y, True, site)
            heapq.heappush(self._events, evt)

        while self._events:
            event = heapq.heappop(self._events)
            if not event.valid:
                continue
            if event.is_site:
                self._handle_site_event(event)
            else:
                self._handle_circle_event(event)

        clipped_edges = self._clip_edges(bbox)

        return VoronoiDiagram(
            sites=sites,
            edges=clipped_edges,
            vertices=list(self._vertices),
        )

    def _handle_site_event(self, event: _Event) -> None:
        """Traite un événement de site (nouveau point atteint par le sweep)."""
        p = event.point

        if not self._arcs:
            self._arcs.append(_Arc(p))
            return

        idx = self._find_arc_above(p)
        if idx is None:
            idx = len(self._arcs) - 1

        arc = self._arcs[idx]

        if arc.circle_event:
            arc.circle_event.valid = False
            arc.circle_event = None

        mid_x = p.x
        if abs(arc.site.y - p.y) < EPS:
            mid_x = (arc.site.x + p.x) / 2.0

        left_edge = _HalfEdgeRecord(arc.site, p)
        right_edge = _HalfEdgeRecord(p, arc.site)

        start_y = self._parabola_y(arc.site, p.y, mid_x)
        start_point = Point(mid_x, start_y)
        left_edge.start = start_point
        right_edge.start = start_point

        dx = arc.site.y - p.y
        dy = -(arc.site.x - p.x)
        norm = math.sqrt(dx * dx + dy * dy) if (dx * dx + dy * dy) > 0 else 1.0
        left_edge.direction = (dx / norm, dy / norm)
        right_edge.direction = (-dx / norm, -dy / norm)

        self._edges.append(left_edge)
        self._edges.append(right_edge)

        new_arc = _Arc(p)
        right_copy = _Arc(arc.site)

        new_arc.left_edge = left_edge
        new_arc.right_edge = right_edge
        right_copy.left_edge = right_edge

        if arc.right_edge:
            right_copy.right_edge = arc.right_edge

        arc.right_edge = left_edge

        self._arcs.insert(idx + 1, new_arc)
        self._arcs.insert(idx + 2, right_copy)

        if idx > 0:
            self._check_circle_event(idx, event.y)
        if idx + 2 < len(self._arcs) - 1:
            self._check_circle_event(idx + 2, event.y)

    def _handle_circle_event(self, event: _Event) -> None:
        """Traite un événement de cercle (un arc disparaît)."""
        arc = event.arc
        if arc is None:
            return

        try:
            idx = self._arcs.index(arc)
        except ValueError:
            return

        if idx <= 0 or idx >= len(self._arcs) - 1:
            return

        left_arc = self._arcs[idx - 1]
        right_arc = self._arcs[idx + 1]

        if left_arc.circle_event:
            left_arc.circle_event.valid = False
            left_arc.circle_event = None
        if right_arc.circle_event:
            right_arc.circle_event.valid = False
            right_arc.circle_event = None

        vertex = event.point
        self._vertices.append(vertex)

        if arc.left_edge:
            arc.left_edge.finish(vertex)
        if arc.right_edge:
            arc.right_edge.finish(vertex)

        new_edge = _HalfEdgeRecord(left_arc.site, right_arc.site)
        new_edge.start = vertex

        dx = left_arc.site.y - right_arc.site.y
        dy = -(left_arc.site.x - right_arc.site.x)
        norm = math.sqrt(dx * dx + dy * dy) if (dx * dx + dy * dy) > 0 else 1.0
        new_edge.direction = (dx / norm, dy / norm)

        self._edges.append(new_edge)

        left_arc.right_edge = new_edge
        right_arc.left_edge = new_edge

        self._arcs.pop(idx)

        if idx - 1 > 0:
            self._check_circle_event(idx - 1, event.y)
        if idx < len(self._arcs) - 1:
            self._check_circle_event(idx, event.y)

    def _check_circle_event(self, idx: int, sweep_y: float) -> None:
        """Vérifie si l'arc à l'index donné génère un événement de cercle."""
        if idx <= 0 or idx >= len(self._arcs) - 1:
            return

        arc = self._arcs[idx]
        left = self._arcs[idx - 1]
        right = self._arcs[idx + 1]

        if (
            abs(left.site.x - right.site.x) < EPS
            and abs(left.site.y - right.site.y) < EPS
        ):
            return

        result = self._circumcircle(left.site, arc.site, right.site)
        if result is None:
            return

        center, radius = result
        bottom_y = center.y + radius

        if bottom_y < sweep_y - EPS:
            return

        if arc.circle_event:
            arc.circle_event.valid = False

        evt = _Event(bottom_y, False, center, arc)
        arc.circle_event = evt
        heapq.heappush(self._events, evt)

    def _find_arc_above(self, point: Point) -> Optional[int]:
        """Trouve l'arc directement au-dessus du point donné."""
        if not self._arcs:
            return None

        for i in range(len(self._arcs)):
            x_left = float("-inf")
            x_right = float("inf")

            if i > 0:
                x_left = self._breakpoint_x(
                    self._arcs[i - 1].site, self._arcs[i].site, point.y
                )
            if i < len(self._arcs) - 1:
                x_right = self._breakpoint_x(
                    self._arcs[i].site, self._arcs[i + 1].site, point.y
                )

            if x_left - EPS <= point.x <= x_right + EPS:
                return i

        return len(self._arcs) - 1

    def _breakpoint_x(self, left: Point, right: Point, sweep_y: float) -> float:
        """Calcule la coordonnée x du point de rupture entre deux paraboles."""
        if abs(left.y - right.y) < EPS:
            return (left.x + right.x) / 2.0

        if abs(left.y - sweep_y) < EPS:
            return left.x

        if abs(right.y - sweep_y) < EPS:
            return right.x

        a1 = 1.0 / (2.0 * (left.y - sweep_y))
        a2 = 1.0 / (2.0 * (right.y - sweep_y))

        a = a1 - a2
        b = 2.0 * (right.x * a2 - left.x * a1)
        c = (
            left.x * left.x * a1
            - right.x * right.x * a2
            + 0.5 * (left.y - right.y)
        )

        if abs(a) < EPS:
            if abs(b) < EPS:
                return (left.x + right.x) / 2.0
            return -c / b

        discriminant = b * b - 4.0 * a * c
        if discriminant < 0:
            discriminant = 0.0

        sqrt_disc = math.sqrt(discriminant)
        x1 = (-b + sqrt_disc) / (2.0 * a)
        x2 = (-b - sqrt_disc) / (2.0 * a)

        if left.y > right.y:
            return max(x1, x2)
        return min(x1, x2)

    def _parabola_y(self, focus: Point, directrix_y: float, x: float) -> float:
        """Calcule y sur la parabole définie par le focus et la directrice."""
        if abs(focus.y - directrix_y) < EPS:
            return focus.y

        a = 1.0 / (2.0 * (focus.y - directrix_y))
        return a * (x - focus.x) ** 2 + (focus.y + directrix_y) / 2.0

    @staticmethod
    def _circumcircle(
        a: Point, b: Point, c: Point
    ) -> Optional[tuple[Point, float]]:
        """Calcule le cercle circonscrit de trois points. None si colinéaires."""
        d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))

        if abs(d) < EPS:
            return None

        a_sq = a.x * a.x + a.y * a.y
        b_sq = b.x * b.x + b.y * b.y
        c_sq = c.x * c.x + c.y * c.y

        ux = (a_sq * (b.y - c.y) + b_sq * (c.y - a.y) + c_sq * (a.y - b.y)) / d
        uy = (a_sq * (c.x - b.x) + b_sq * (a.x - c.x) + c_sq * (b.x - a.x)) / d

        center = Point(ux, uy)
        radius = math.sqrt((a.x - ux) ** 2 + (a.y - uy) ** 2)

        return center, radius

    def _clip_edges(self, bbox: BoundingBox) -> list[Edge]:
        """Clippe toutes les arêtes aux limites de la bounding box."""
        result: list[Edge] = []
        margin = max(bbox.width, bbox.height) * 10

        for he in self._edges:
            if he.start is None:
                continue

            if he.end is not None:
                p1, p2 = he.start, he.end
            else:
                dx, dy = he.direction
                p1 = he.start
                p2 = Point(p1.x + dx * margin, p1.y + dy * margin)

            clipped = bbox.clip_segment(p1, p2)
            if clipped:
                cp1, cp2 = clipped
                if cp1.distance_sq(cp2) > EPS:
                    result.append(Edge(cp1, cp2))

        return result
