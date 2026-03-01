"""Tests pour l'algorithme brute force de Voronoi."""

import math
import pytest

from voronoi.core.geometry import Point, BoundingBox
from voronoi.core.brute_force import BruteForceVoronoi


class TestBruteForceVoronoi:
    def setup_method(self):
        self.algo = BruteForceVoronoi()

    def test_single_point(self, standard_bbox):
        """Un seul point : tous les pixels lui sont assignés."""
        sites = [Point(400, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert diagram.pixel_assignments is not None
        assert diagram.width == 800
        assert diagram.height == 600

        for row in diagram.pixel_assignments:
            for val in row:
                assert val == 0

    def test_two_points_bisector(self, standard_bbox):
        """Deux points horizontaux : la frontière est la médiatrice verticale."""
        sites = [Point(200, 300), Point(600, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert diagram.pixel_assignments is not None

        # Au milieu (x=400), le pixel devrait être à la frontière
        # Les pixels à gauche du milieu appartiennent au site 0
        assert diagram.pixel_assignments[300][100] == 0
        # Les pixels à droite du milieu appartiennent au site 1
        assert diagram.pixel_assignments[300][700] == 1

    def test_two_points_vertical_bisector(self, standard_bbox):
        """Deux points verticaux : la frontière est la médiatrice horizontale."""
        sites = [Point(400, 100), Point(400, 500)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert diagram.pixel_assignments is not None

        # En haut -> site 0
        assert diagram.pixel_assignments[50][400] == 0
        # En bas -> site 1
        assert diagram.pixel_assignments[550][400] == 1

    def test_three_points_assignments(self, standard_bbox):
        """Trois points : chaque pixel est assigné au plus proche."""
        sites = [Point(100, 100), Point(700, 100), Point(400, 500)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert diagram.pixel_assignments is not None

        # Coin haut-gauche -> site 0
        assert diagram.pixel_assignments[50][50] == 0
        # Coin haut-droit -> site 1
        assert diagram.pixel_assignments[50][750] == 1
        # En bas au milieu -> site 2
        assert diagram.pixel_assignments[550][400] == 2

    def test_empty_sites(self, standard_bbox):
        """Aucun site : résultat vide."""
        diagram = self.algo.compute([], standard_bbox)
        assert diagram.pixel_assignments is None
        assert diagram.width == 800

    def test_edges_exist(self, standard_bbox):
        """Avec deux points, des arêtes frontières sont détectées."""
        sites = [Point(200, 300), Point(600, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert len(diagram.edges) > 0

    def test_collinear_points(self, collinear_points, standard_bbox):
        """Points colinéaires : les frontières sont des lignes verticales."""
        diagram = self.algo.compute(collinear_points, standard_bbox)
        assert diagram.pixel_assignments is not None

        # Point gauche (x=100) : pixel à x=50 lui est assigné
        assert diagram.pixel_assignments[300][50] == 0
        # Point milieu (x=400) : pixel à x=400 lui est assigné
        assert diagram.pixel_assignments[300][400] == 1
        # Point droit (x=700) : pixel à x=750 lui est assigné
        assert diagram.pixel_assignments[300][750] == 2

    def test_nearest_neighbor_correctness(self, standard_bbox):
        """Vérifie que chaque pixel est bien assigné au site le plus proche."""
        sites = [Point(150, 200), Point(500, 100), Point(300, 450), Point(650, 400)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert diagram.pixel_assignments is not None

        # Vérification sur un échantillon de pixels
        test_pixels = [
            (50, 100), (700, 50), (250, 500), (600, 350),
            (400, 300), (100, 400), (750, 550),
        ]

        for px, py in test_pixels:
            assigned = diagram.pixel_assignments[py][px]
            min_d = float("inf")
            expected = -1
            for i, s in enumerate(sites):
                d = (px - s.x) ** 2 + (py - s.y) ** 2
                if d < min_d:
                    min_d = d
                    expected = i
            assert assigned == expected, (
                f"Pixel ({px},{py}): assigné={assigned}, attendu={expected}"
            )
