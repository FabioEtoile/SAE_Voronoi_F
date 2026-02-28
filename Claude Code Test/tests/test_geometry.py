"""Tests pour les primitives géométriques."""

import math
import pytest

from voronoi.core.geometry import Point, Edge, BoundingBox


class TestPoint:
    def test_distance_to_self(self):
        p = Point(3.0, 4.0)
        assert p.distance_to(p) == 0.0

    def test_distance_to_origin(self):
        p = Point(3.0, 4.0)
        origin = Point(0.0, 0.0)
        assert math.isclose(p.distance_to(origin), 5.0)

    def test_distance_sq(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert p1.distance_sq(p2) == 25.0

    def test_distance_symmetric(self):
        p1 = Point(1, 2)
        p2 = Point(5, 8)
        assert math.isclose(p1.distance_to(p2), p2.distance_to(p1))

    def test_frozen(self):
        p = Point(1, 2)
        with pytest.raises(AttributeError):
            p.x = 5  # type: ignore

    def test_iter(self):
        p = Point(3.0, 7.0)
        x, y = p
        assert x == 3.0
        assert y == 7.0


class TestEdge:
    def test_length_horizontal(self):
        e = Edge(Point(0, 0), Point(10, 0))
        assert math.isclose(e.length(), 10.0)

    def test_length_diagonal(self):
        e = Edge(Point(0, 0), Point(3, 4))
        assert math.isclose(e.length(), 5.0)

    def test_length_zero(self):
        e = Edge(Point(5, 5), Point(5, 5))
        assert e.length() == 0.0


class TestBoundingBox:
    def test_contains_inside(self):
        bbox = BoundingBox(0, 0, 100, 100)
        assert bbox.contains(Point(50, 50))

    def test_contains_on_edge(self):
        bbox = BoundingBox(0, 0, 100, 100)
        assert bbox.contains(Point(0, 50))
        assert bbox.contains(Point(100, 50))

    def test_not_contains_outside(self):
        bbox = BoundingBox(0, 0, 100, 100)
        assert not bbox.contains(Point(-1, 50))
        assert not bbox.contains(Point(50, 101))

    def test_width_height(self):
        bbox = BoundingBox(10, 20, 110, 120)
        assert bbox.width == 100
        assert bbox.height == 100

    def test_clip_segment_inside(self):
        bbox = BoundingBox(0, 0, 100, 100)
        result = bbox.clip_segment(Point(20, 20), Point(80, 80))
        assert result is not None
        p1, p2 = result
        assert math.isclose(p1.x, 20)
        assert math.isclose(p2.x, 80)

    def test_clip_segment_crossing(self):
        bbox = BoundingBox(0, 0, 100, 100)
        result = bbox.clip_segment(Point(-50, 50), Point(150, 50))
        assert result is not None
        p1, p2 = result
        assert math.isclose(p1.x, 0)
        assert math.isclose(p2.x, 100)

    def test_clip_segment_outside(self):
        bbox = BoundingBox(0, 0, 100, 100)
        result = bbox.clip_segment(Point(200, 200), Point(300, 300))
        assert result is None
