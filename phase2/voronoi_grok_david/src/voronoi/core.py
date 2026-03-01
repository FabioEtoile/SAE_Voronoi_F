import math
from typing import List, Tuple

try:
    import numpy as np
    from scipy.spatial import Voronoi
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"

    def distance_to(self, other: 'Point') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


def get_bbox(points: List[Point], margin: float = 0.5) -> Tuple[float, float, float, float]:
    if not points:
        return 0.0, 0.0, 100.0, 100.0
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    w = xmax - xmin or 100.0
    h = ymax - ymin or 100.0
    xmin -= margin * w
    xmax += margin * w
    ymin -= margin * h
    ymax += margin * h
    return xmin, ymin, xmax, ymax


def sort_polygon(poly: List[Point]) -> List[Point]:
    if len(poly) < 3:
        return poly
    cx = sum(p.x for p in poly) / len(poly)
    cy = sum(p.y for p in poly) / len(poly)
    def angle_key(p):
        return math.atan2(p.y - cy, p.x - cx)
    sorted_poly = sorted(poly, key=angle_key)
    if len(sorted_poly) > 1 and sorted_poly[0].distance_to(sorted_poly[-1]) < 1e-6:
        sorted_poly.pop()
    return sorted_poly


def compute_voronoi_cells(points: List[Point], bbox: Tuple[float, float, float, float]) -> List[List[Point]]:
    if not SCIPY_AVAILABLE:
        raise ImportError("pip install scipy numpy")

    if len(points) < 2:
        return [[] for _ in points]

    # Ajout de 4 points fictifs très loin pour forcer toutes les cellules à être bornées
    xmin, ymin, xmax, ymax = bbox
    far = max(xmax - xmin, ymax - ymin) * 10
    dummy = [
        Point(xmin - far, ymin - far),
        Point(xmax + far, ymin - far),
        Point(xmax + far, ymax + far),
        Point(xmin - far, ymax + far)
    ]

    all_points = points + dummy
    pts = np.array([[p.x, p.y] for p in all_points])
    vor = Voronoi(pts)

    cells = []
    for i in range(len(points)):  # seulement les vrais points
        region = vor.regions[vor.point_region[i]]
        poly = []
        for v_idx in region:
            if v_idx == -1:
                continue
            vx, vy = vor.vertices[v_idx]
            poly.append(Point(vx, vy))
        if len(poly) >= 3:
            poly = sort_polygon(poly)
        cells.append(poly)

    return cells