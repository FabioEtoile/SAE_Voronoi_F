"""Tests pour l'algorithme de Fortune."""

import math
import pytest

from voronoi.core.geometry import Point, BoundingBox, Edge
from voronoi.core.fortune import FortuneVoronoi


class TestFortuneVoronoi:
    def setup_method(self):
        self.algo = FortuneVoronoi()

    def test_two_points_produces_edge(self, standard_bbox):
        """Deux points doivent produire au moins une arête (la médiatrice)."""
        sites = [Point(200, 300), Point(600, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert len(diagram.edges) >= 1

    def test_two_points_bisector_midpoint(self, standard_bbox):
        """L'arête entre deux points passe par le milieu."""
        sites = [Point(200, 300), Point(600, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        # Au moins une arête doit passer près de x=400
        midpoint_x = 400.0
        found_near_midpoint = False
        for edge in diagram.edges:
            mid_edge_x = (edge.start.x + edge.end.x) / 2.0
            if abs(mid_edge_x - midpoint_x) < 50:
                found_near_midpoint = True
                break

        assert found_near_midpoint, "Aucune arête ne passe près du milieu"

    def test_three_points_vertex(self, standard_bbox):
        """Trois points non colinéaires produisent au moins un sommet."""
        sites = [Point(400, 100), Point(200, 500), Point(600, 500)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert len(diagram.vertices) >= 1

    def test_three_points_vertex_equidistant(self, standard_bbox):
        """Le sommet de Voronoi est équidistant des trois sites."""
        sites = [Point(400, 100), Point(200, 500), Point(600, 500)]
        diagram = self.algo.compute(sites, standard_bbox)

        if diagram.vertices:
            vertex = diagram.vertices[0]
            d0 = vertex.distance_to(sites[0])
            d1 = vertex.distance_to(sites[1])
            d2 = vertex.distance_to(sites[2])

            assert math.isclose(d0, d1, rel_tol=0.01), (
                f"Distances non égales: d0={d0}, d1={d1}"
            )
            assert math.isclose(d1, d2, rel_tol=0.01), (
                f"Distances non égales: d1={d1}, d2={d2}"
            )

    def test_single_point_no_edges(self, standard_bbox):
        """Un seul point ne produit aucune arête."""
        sites = [Point(400, 300)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert len(diagram.edges) == 0

    def test_edge_count_upper_bound(self, standard_bbox):
        """Le nombre d'arêtes respecte la borne d'Euler : <= 3n - 6."""
        sites = [
            Point(100, 100), Point(700, 100), Point(400, 300),
            Point(200, 500), Point(600, 500), Point(100, 300),
            Point(700, 300), Point(400, 500),
        ]
        diagram = self.algo.compute(sites, standard_bbox)

        n = len(sites)
        max_edges = 3 * n - 6 + n  # arêtes finies + semi-infinies
        assert len(diagram.edges) <= max_edges

    def test_many_points_no_crash(self, standard_bbox):
        """L'algorithme ne plante pas avec beaucoup de points."""
        import random
        random.seed(42)
        sites = [Point(random.uniform(50, 750), random.uniform(50, 550)) for _ in range(50)]
        diagram = self.algo.compute(sites, standard_bbox)

        assert len(diagram.edges) > 0
        assert len(diagram.vertices) > 0

    def test_duplicate_points_handled(self, standard_bbox):
        """Les points en double sont gérés sans crash."""
        sites = [Point(400, 300), Point(400, 300), Point(200, 200)]
        diagram = self.algo.compute(sites, standard_bbox)
        # Ne doit pas planter
        assert diagram is not None

    def test_edges_within_bbox(self, standard_bbox):
        """Toutes les arêtes clippées sont dans la bounding box."""
        sites = [
            Point(200, 200), Point(600, 200),
            Point(200, 400), Point(600, 400),
        ]
        diagram = self.algo.compute(sites, standard_bbox)

        for edge in diagram.edges:
            assert -1 <= edge.start.x <= 801
            assert -1 <= edge.start.y <= 601
            assert -1 <= edge.end.x <= 801
            assert -1 <= edge.end.y <= 601

    def test_circumcircle_collinear(self):
        """Trois points colinéaires : pas de cercle circonscrit."""
        result = FortuneVoronoi._circumcircle(
            Point(0, 0), Point(1, 1), Point(2, 2)
        )
        assert result is None

    def test_circumcircle_right_triangle(self):
        """Triangle rectangle : le centre du cercle est au milieu de l'hypoténuse."""
        result = FortuneVoronoi._circumcircle(
            Point(0, 0), Point(4, 0), Point(0, 3)
        )
        assert result is not None
        center, radius = result
        assert math.isclose(center.x, 2.0, abs_tol=1e-6)
        assert math.isclose(center.y, 1.5, abs_tol=1e-6)
        assert math.isclose(radius, 2.5, abs_tol=1e-6)
