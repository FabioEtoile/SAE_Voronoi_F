"""
Voronoi Diagram - Fortune's Sweep Line Algorithm
Implementation from scratch without Voronoi-specific libraries.
Uses only math, heapq, and basic data structures.
"""

import math
import heapq
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

@dataclass
class Point:
    x: float
    y: float

    def __eq__(self, other):
        return isinstance(other, Point) and abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"Point({self.x:.3f}, {self.y:.3f})"


@dataclass
class Edge:
    """A half-edge in the DCEL, representing a segment of a Voronoi edge."""
    start: Optional[Point] = None
    end: Optional[Point] = None
    left_site: Optional[Point] = None   # site to the left
    right_site: Optional[Point] = None  # site to the right

    def is_complete(self) -> bool:
        return self.start is not None and self.end is not None

    def length(self) -> float:
        if not self.is_complete():
            return 0.0
        return self.start.distance_to(self.end)

    def clipped(self, x_min: float, y_min: float, x_max: float, y_max: float) -> Optional["Edge"]:
        """Clip edge to bounding box using Cohen-Sutherland algorithm."""
        if not self.is_complete():
            return None
        p1, p2 = self.start, self.end
        result = _cohen_sutherland(p1.x, p1.y, p2.x, p2.y, x_min, y_min, x_max, y_max)
        if result is None:
            return None
        x1, y1, x2, y2 = result
        return Edge(Point(x1, y1), Point(x2, y2), self.left_site, self.right_site)


# ---------------------------------------------------------------------------
# Cohen-Sutherland line clipping
# ---------------------------------------------------------------------------

_INSIDE, _LEFT, _RIGHT, _BOTTOM, _TOP = 0, 1, 2, 4, 8


def _compute_code(x, y, x_min, y_min, x_max, y_max):
    code = _INSIDE
    if x < x_min:
        code |= _LEFT
    elif x > x_max:
        code |= _RIGHT
    if y < y_min:
        code |= _BOTTOM
    elif y > y_max:
        code |= _TOP
    return code


def _cohen_sutherland(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    """Returns clipped (x1,y1,x2,y2) or None if entirely outside."""
    c1 = _compute_code(x1, y1, x_min, y_min, x_max, y_max)
    c2 = _compute_code(x2, y2, x_min, y_min, x_max, y_max)
    for _ in range(20):  # max iterations
        if not (c1 | c2):
            return x1, y1, x2, y2
        if c1 & c2:
            return None
        c_out = c1 if c1 else c2
        dx, dy = x2 - x1, y2 - y1
        if c_out & _TOP:
            if abs(dy) < 1e-12:
                return None
            x = x1 + dx * (y_max - y1) / dy
            y = y_max
        elif c_out & _BOTTOM:
            if abs(dy) < 1e-12:
                return None
            x = x1 + dx * (y_min - y1) / dy
            y = y_min
        elif c_out & _RIGHT:
            if abs(dx) < 1e-12:
                return None
            y = y1 + dy * (x_max - x1) / dx
            x = x_max
        else:  # LEFT
            if abs(dx) < 1e-12:
                return None
            y = y1 + dy * (x_min - x1) / dx
            x = x_min
        if c_out == c1:
            x1, y1 = x, y
            c1 = _compute_code(x1, y1, x_min, y_min, x_max, y_max)
        else:
            x2, y2 = x, y
            c2 = _compute_code(x2, y2, x_min, y_min, x_max, y_max)
    return None


# ---------------------------------------------------------------------------
# Fortune's Algorithm data structures
# ---------------------------------------------------------------------------

class _Arc:
    """Arc of a parabola in the beach line (linked list node)."""
    __slots__ = ('site', 'prev', 'next', 'event', 'edge_left', 'edge_right')

    def __init__(self, site: Point):
        self.site = site
        self.prev: Optional["_Arc"] = None
        self.next: Optional["_Arc"] = None
        self.event: Optional["_CircleEvent"] = None
        self.edge_left: Optional[Edge] = None   # half-edge to the left
        self.edge_right: Optional[Edge] = None  # half-edge to the right


@dataclass
class _SiteEvent:
    y: float
    x: float
    site: Point

    def __lt__(self, other):
        return (self.y, self.x) < (other.y, other.x)

    def __le__(self, other):
        return (self.y, self.x) <= (other.y, other.x)

    def __eq__(self, other):
        return (self.y, self.x) == (other.y, other.x)


@dataclass
class _CircleEvent:
    y: float          # lowest point of circle (event y)
    x: float          # x of lowest point (tiebreak)
    arc: "_Arc"
    center: Point
    valid: bool = True

    def __lt__(self, other):
        return (self.y, self.x) < (other.y, other.x)

    def __le__(self, other):
        return (self.y, self.x) <= (other.y, other.x)

    def __eq__(self, other):
        return (self.y, self.x) == (other.y, other.x)


# ---------------------------------------------------------------------------
# Fortune's Sweep Line
# ---------------------------------------------------------------------------

class Fortune:
    """Fortune's sweep line Voronoi diagram algorithm."""

    def __init__(self, sites: list[Point]):
        if len(sites) < 2:
            raise ValueError("At least 2 sites required.")
        # Remove duplicates
        self._sites = list({(p.x, p.y): p for p in sites}.values())
        self._edges: list[Edge] = []
        self._pq: list = []   # min-heap of events
        self._beach: Optional[_Arc] = None  # leftmost arc

    # ------------------------------------------------------------------
    def compute(self) -> list[Edge]:
        """Run Fortune's algorithm and return list of Voronoi edges."""
        self._edges = []
        self._pq = []
        self._beach = None

        for site in self._sites:
            heapq.heappush(self._pq, _SiteEvent(site.y, site.x, site))

        while self._pq:
            event = heapq.heappop(self._pq)
            if isinstance(event, _SiteEvent):
                self._handle_site(event.site)
            elif isinstance(event, _CircleEvent):
                if event.valid:
                    self._handle_circle(event)

        self._finish_edges()
        return self._edges

    # ------------------------------------------------------------------
    # Site event: insert new arc into beach line
    # ------------------------------------------------------------------

    def _handle_site(self, site: Point):
        if self._beach is None:
            self._beach = _Arc(site)
            return

        # Find the arc directly above the site
        arc = self._arc_above(site)

        # Invalidate existing circle event for arc
        if arc.event:
            arc.event.valid = False
            arc.event = None

        # Create new edge between arc.site and site
        edge = Edge(start=None, end=None, left_site=arc.site, right_site=site)
        self._edges.append(edge)

        # Split arc into [arc, new_arc, arc_copy]
        arc_copy = _Arc(arc.site)
        new_arc = _Arc(site)

        # Link: ... <-> arc <-> new_arc <-> arc_copy <-> ...
        arc_copy.next = arc.next
        if arc_copy.next:
            arc_copy.next.prev = arc_copy
        arc_copy.prev = new_arc
        new_arc.next = arc_copy
        new_arc.prev = arc
        arc.next = new_arc

        # Each pair shares the same edge (one endpoint will be set)
        arc.edge_right = edge
        new_arc.edge_left = edge
        # Create second edge for the right side (arc_copy.site same as arc.site)
        edge2 = Edge(start=None, end=None, left_site=site, right_site=arc_copy.site)
        self._edges.append(edge2)
        new_arc.edge_right = edge2
        arc_copy.edge_left = edge2

        # Compute starting point: intersection of both parabolas at sweep line
        start = self._parabola_intersection(arc.site, site, site.y)
        edge.start = start
        edge2.start = start

        # Check for new circle events
        self._check_circle(arc)
        self._check_circle(arc_copy)

    # ------------------------------------------------------------------
    # Circle event: remove arc from beach line
    # ------------------------------------------------------------------

    def _handle_circle(self, event: _CircleEvent):
        arc = event.arc
        center = event.center
        vertex = Point(center.x, event.y)  # bottom of circle

        # Invalidate neighbours
        if arc.prev and arc.prev.event:
            arc.prev.event.valid = False
            arc.prev.event = None
        if arc.next and arc.next.event:
            arc.next.event.valid = False
            arc.next.event = None

        # Finish edges touching this arc
        if arc.edge_left:
            arc.edge_left.end = vertex
        if arc.edge_right:
            arc.edge_right.end = vertex

        # Create new edge between arc.prev.site and arc.next.site
        if arc.prev and arc.next:
            # Consistent ordering: left is the site to the geometric left
            # at the vertex, determined by x-position of sites
            ls, rs = arc.prev.site, arc.next.site
            new_edge = Edge(start=vertex, end=None, left_site=ls, right_site=rs)
            self._edges.append(new_edge)
            arc.prev.edge_right = new_edge
            arc.next.edge_left = new_edge

        # Remove arc from beach line
        if arc.prev:
            arc.prev.next = arc.next
        if arc.next:
            arc.next.prev = arc.prev

        # Check new circle events for neighbors
        if arc.prev:
            self._check_circle(arc.prev)
        if arc.next:
            self._check_circle(arc.next)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _arc_above(self, site: Point) -> _Arc:
        """Find arc on beach line directly above the given site."""
        arc = self._beach
        while arc:
            left = self._break_point_x(arc.prev, arc, site.y) if arc.prev else -math.inf
            right = self._break_point_x(arc, arc.next, site.y) if arc.next else math.inf
            if left <= site.x <= right:
                return arc
            arc = arc.next
        # Fallback (shouldn't happen with correct beach line)
        arc = self._beach
        while arc.next:
            arc = arc.next
        return arc

    def _break_point_x(self, left_arc: Optional[_Arc], right_arc: Optional[_Arc], sweep_y: float) -> float:
        """X coordinate of the breakpoint between two arcs."""
        if left_arc is None or right_arc is None:
            return math.inf
        return self._parabola_intersection(left_arc.site, right_arc.site, sweep_y).x

    def _parabola_intersection(self, p1: Point, p2: Point, sweep_y: float) -> Point:
        """Intersection point of two parabolas defined by sites p1,p2 and sweep line."""
        # Handle degenerate cases
        if abs(p1.y - p2.y) < 1e-10:
            return Point((p1.x + p2.x) / 2, sweep_y)

        if abs(p1.y - sweep_y) < 1e-10:
            x = p1.x
            y = (x * x - 2 * p2.x * x + p2.x ** 2 + p2.y ** 2 - sweep_y ** 2) / (2 * (p2.y - sweep_y))
            return Point(x, y)

        if abs(p2.y - sweep_y) < 1e-10:
            x = p2.x
            y = (x * x - 2 * p1.x * x + p1.x ** 2 + p1.y ** 2 - sweep_y ** 2) / (2 * (p1.y - sweep_y))
            return Point(x, y)

        a1 = 1 / (2 * (p1.y - sweep_y))
        a2 = 1 / (2 * (p2.y - sweep_y))
        b1 = -p1.x * a1
        b2 = -p2.x * a2
        c1 = a1 * p1.x ** 2 + (p1.y ** 2 - sweep_y ** 2) / (2 * (p1.y - sweep_y))
        c2 = a2 * p2.x ** 2 + (p2.y ** 2 - sweep_y ** 2) / (2 * (p2.y - sweep_y))

        da = a1 - a2
        db = b1 - b2
        dc = c1 - c2

        if abs(da) < 1e-12:
            if abs(db) < 1e-12:
                return Point((p1.x + p2.x) / 2, sweep_y)
            x = -dc / db
        else:
            discriminant = db ** 2 - 4 * da * dc
            discriminant = max(0.0, discriminant)
            sqrt_d = math.sqrt(discriminant)
            x1 = (-db + sqrt_d) / (2 * da)
            x2 = (-db - sqrt_d) / (2 * da)
            x = x1 if p1.y < p2.y else x2

        y = a1 * x ** 2 + b1 * x + c1
        return Point(x, y)

    def _check_circle(self, arc: _Arc):
        """Check if three consecutive arcs form a converging circle event."""
        if arc.prev is None or arc.next is None:
            return
        a, b, c = arc.prev.site, arc.site, arc.next.site
        center = _circumcenter(a, b, c)
        if center is None:
            return
        # Check that the sweep has not yet passed the bottom of the circle
        r = a.distance_to(center)
        bottom_y = center.y + r
        if bottom_y < arc.site.y - 1e-10:
            return
        event = _CircleEvent(y=bottom_y, x=center.x, arc=arc, center=center)
        arc.event = event
        heapq.heappush(self._pq, event)

    def _finish_edges(self):
        """Extend or close edges that reach to infinity using a large bounding box."""
        # Compute bounding box of sites
        xs = [s.x for s in self._sites]
        ys = [s.y for s in self._sites]
        margin = max(max(xs) - min(xs), max(ys) - min(ys)) * 2 + 200
        x_min, x_max = min(xs) - margin, max(xs) + margin
        y_min, y_max = min(ys) - margin, max(ys) + margin

        arc = self._beach
        while arc and arc.next:
            if arc.edge_right and arc.edge_right.end is None:
                # Direction: perpendicular bisector direction
                p1, p2 = arc.site, arc.next.site
                mx, my = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
                dx, dy = p2.y - p1.y, -(p2.x - p1.x)
                norm = math.hypot(dx, dy)
                if norm > 1e-12:
                    dx, dy = dx / norm * margin, dy / norm * margin
                arc.edge_right.end = Point(mx + dx, my + dy)
            arc = arc.next


def _circumcenter(a: Point, b: Point, c: Point) -> Optional[Point]:
    """Circumcenter of triangle abc, or None if collinear."""
    ax, ay = b.x - a.x, b.y - a.y
    bx, by = c.x - a.x, c.y - a.y
    D = 2 * (ax * by - ay * bx)
    if abs(D) < 1e-12:
        return None
    ux = (by * (ax ** 2 + ay ** 2) - ay * (bx ** 2 + by ** 2)) / D
    uy = (ax * (bx ** 2 + by ** 2) - bx * (ax ** 2 + ay ** 2)) / D
    return Point(a.x + ux, a.y + uy)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class VoronoiDiagram:
    """High-level Voronoi diagram builder."""

    def __init__(self, sites: list[Point]):
        self.sites = sites
        self._raw_edges: list[Edge] = []
        self._clipped_edges: list[Edge] = []
        self.bbox: tuple[float, float, float, float] = (0, 0, 0, 0)

    def compute(self, margin: float = 50.0):
        """Compute the diagram and clip to bounding box + margin."""
        if not self.sites:
            raise ValueError("No sites provided.")

        xs = [s.x for s in self.sites]
        ys = [s.y for s in self.sites]
        self.bbox = (
            min(xs) - margin,
            min(ys) - margin,
            max(xs) + margin,
            max(ys) + margin,
        )

        f = Fortune(self.sites)
        self._raw_edges = f.compute()
        self._clip()

    def _clip(self):
        x_min, y_min, x_max, y_max = self.bbox
        self._clipped_edges = []
        for edge in self._raw_edges:
            clipped = edge.clipped(x_min, y_min, x_max, y_max)
            if clipped is not None and clipped.length() > 1e-6:
                self._clipped_edges.append(clipped)

    @property
    def edges(self) -> list[Edge]:
        return self._clipped_edges

    @property
    def raw_edges(self) -> list[Edge]:
        return self._raw_edges


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

def parse_points_file(filepath: str) -> list[Point]:
    """Parse a text file where each line is 'x,y'."""
    points = []
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 2:
                raise ValueError(f"Line {lineno}: expected 'x,y', got {line!r}")
            try:
                x, y = float(parts[0].strip()), float(parts[1].strip())
            except ValueError:
                raise ValueError(f"Line {lineno}: cannot parse numbers in {line!r}")
            points.append(Point(x, y))
    if len(points) < 2:
        raise ValueError("File must contain at least 2 points.")
    return points
