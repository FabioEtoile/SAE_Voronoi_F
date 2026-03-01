from typing import List
from core.point import Point
from core.geometry import perpendicular_bisector, clip_polygon

class VoronoiDiagram:

    def __init__(self, points: List[Point], width=500, height=500):
        self.points = points
        self.width = width
        self.height = height

    def compute(self):
        cells = {}

        for pi in self.points:
            polygon = [
                Point(0, 0),
                Point(self.width, 0),
                Point(self.width, self.height),
                Point(0, self.height)
            ]

            for pj in self.points:
                if pi == pj:
                    continue

                mid, normal = perpendicular_bisector(pi, pj)

                # garder côté contenant pi
                if (pi.x - mid.x)*normal.x + (pi.y - mid.y)*normal.y < 0:
                    normal = Point(-normal.x, -normal.y)

                polygon = clip_polygon(polygon, mid, normal)

            cells[pi] = polygon

        return cells