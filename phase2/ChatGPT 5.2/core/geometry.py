from typing import List
from core.point import Point

def midpoint(p1: Point, p2: Point) -> Point:
    return Point((p1.x + p2.x)/2, (p1.y + p2.y)/2)

def perpendicular_bisector(p1: Point, p2: Point):
    mid = midpoint(p1, p2)
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return mid, Point(dx, dy)

def clip_polygon(polygon: List[Point], line_point: Point, normal: Point) -> List[Point]:
    result = []
    for i in range(len(polygon)):
        current = polygon[i]
        next_point = polygon[(i+1) % len(polygon)]

        current_side = (current.x - line_point.x)*normal.x + (current.y - line_point.y)*normal.y
        next_side = (next_point.x - line_point.x)*normal.x + (next_point.y - line_point.y)*normal.y

        if current_side >= 0:
            result.append(current)

        if current_side * next_side < 0:
            t = current_side / (current_side - next_side)
            ix = current.x + t*(next_point.x - current.x)
            iy = current.y + t*(next_point.y - current.y)
            result.append(Point(ix, iy))

    return result