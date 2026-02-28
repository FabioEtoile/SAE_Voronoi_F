"""Fixtures partagées pour les tests."""

import pytest

from voronoi.core.geometry import Point, BoundingBox


@pytest.fixture
def two_points() -> list[Point]:
    """Deux points simples pour le cas de base."""
    return [Point(200, 300), Point(600, 300)]


@pytest.fixture
def three_points() -> list[Point]:
    """Trois points formant un triangle."""
    return [Point(400, 100), Point(200, 500), Point(600, 500)]


@pytest.fixture
def collinear_points() -> list[Point]:
    """Trois points colinéaires (horizontaux)."""
    return [Point(100, 300), Point(400, 300), Point(700, 300)]


@pytest.fixture
def sample_points() -> list[Point]:
    """Points d'exemple du fichier small.txt."""
    return [
        Point(213, 247),
        Point(54, 424),
        Point(180, 29),
        Point(212, 237),
        Point(50, 370),
    ]


@pytest.fixture
def standard_bbox() -> BoundingBox:
    """Bounding box standard 800x600."""
    return BoundingBox(0, 0, 800, 600)
