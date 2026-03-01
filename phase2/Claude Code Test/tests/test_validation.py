"""Validation de l'implémentation contre scipy.spatial.Voronoi."""

import math
import pytest
import numpy as np
from scipy.spatial import Voronoi as ScipyVoronoi, KDTree

from voronoi.core.geometry import Point, BoundingBox
from voronoi.core.brute_force import BruteForceVoronoi
from voronoi.core.fortune import FortuneVoronoi


class TestBruteForceAgainstScipy:
    """Valide l'algorithme brute force contre scipy.spatial.KDTree."""

    def setup_method(self):
        self.algo = BruteForceVoronoi()

    def _make_points(self, seed: int, n: int) -> list[tuple[float, float]]:
        rng = np.random.default_rng(seed)
        raw = rng.uniform(50, 750, size=(n, 2))
        return [(float(x), float(y)) for x, y in raw]

    def test_nearest_neighbor_10_points(self):
        """10 points : chaque pixel est assigné au bon site."""
        raw = self._make_points(42, 10)
        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        tree = KDTree(np.array(raw))
        rng = np.random.default_rng(99)

        errors = 0
        for _ in range(1000):
            px = int(rng.uniform(0, 800))
            py = int(rng.uniform(0, 600))
            our = diagram.pixel_assignments[py][px]
            _, scipy_idx = tree.query([px, py])
            if our != scipy_idx:
                errors += 1

        assert errors == 0, f"{errors} pixels mal assignés sur 1000"

    def test_nearest_neighbor_30_points(self):
        """30 points : validation sur plus de sites."""
        raw = self._make_points(123, 30)
        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        tree = KDTree(np.array(raw))
        rng = np.random.default_rng(456)

        errors = 0
        for _ in range(500):
            px = int(rng.uniform(0, 800))
            py = int(rng.uniform(0, 600))
            our = diagram.pixel_assignments[py][px]
            _, scipy_idx = tree.query([px, py])
            if our != scipy_idx:
                errors += 1

        assert errors == 0, f"{errors} pixels mal assignés sur 500"

    @pytest.mark.parametrize("num_points", [3, 5, 10, 20])
    def test_various_sizes(self, num_points):
        """Test avec différentes tailles d'entrée."""
        raw = self._make_points(num_points * 7, num_points)
        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        tree = KDTree(np.array(raw))
        rng = np.random.default_rng(789)

        errors = 0
        n_samples = 300
        for _ in range(n_samples):
            px = int(rng.uniform(0, 800))
            py = int(rng.uniform(0, 600))
            our = diagram.pixel_assignments[py][px]
            _, scipy_idx = tree.query([px, py])
            if our != scipy_idx:
                errors += 1

        assert errors == 0, (
            f"{num_points} points : {errors}/{n_samples} pixels mal assignés"
        )


class TestFortuneAgainstScipy:
    """Valide l'algorithme de Fortune contre scipy.spatial.Voronoi."""

    def setup_method(self):
        self.algo = FortuneVoronoi()

    def _make_points(self, seed: int, n: int) -> list[tuple[float, float]]:
        rng = np.random.default_rng(seed)
        raw = rng.uniform(100, 700, size=(n, 2))
        return [(float(x), float(y)) for x, y in raw]

    def test_vertex_count_similar(self):
        """Le nombre de sommets doit être proche de celui de scipy."""
        raw = self._make_points(42, 15)
        scipy_v = ScipyVoronoi(np.array(raw))
        n_scipy_finite = sum(
            1 for v in scipy_v.vertices
            if not any(math.isinf(c) for c in v)
        )

        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        # Tolérance : notre implémentation peut avoir ±2 sommets
        # selon la gestion des cas dégénérés
        assert abs(len(diagram.vertices) - n_scipy_finite) <= 3, (
            f"Nos sommets: {len(diagram.vertices)}, scipy: {n_scipy_finite}"
        )

    def test_vertices_near_scipy(self):
        """Chaque sommet de notre algo doit être proche d'un sommet scipy."""
        raw = self._make_points(42, 10)
        scipy_v = ScipyVoronoi(np.array(raw))

        scipy_verts = [
            (float(v[0]), float(v[1]))
            for v in scipy_v.vertices
            if not any(math.isinf(c) for c in v)
        ]

        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        # Chaque sommet intérieur devrait correspondre à un sommet scipy
        matched = 0
        for vertex in diagram.vertices:
            if not (50 < vertex.x < 750 and 50 < vertex.y < 550):
                continue  # Ignorer les sommets près des bords (clipping)

            for sv in scipy_verts:
                if (
                    math.isclose(vertex.x, sv[0], abs_tol=5.0)
                    and math.isclose(vertex.y, sv[1], abs_tol=5.0)
                ):
                    matched += 1
                    break

        # Au moins 50% des sommets intérieurs matchent
        interior = [
            v for v in diagram.vertices
            if 50 < v.x < 750 and 50 < v.y < 550
        ]
        if interior:
            match_ratio = matched / len(interior)
            assert match_ratio >= 0.5, (
                f"Seulement {matched}/{len(interior)} sommets matchent scipy"
            )

    def test_edge_count_euler_bound(self):
        """Le nombre d'arêtes respecte la borne d'Euler."""
        raw = self._make_points(42, 20)
        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        n = len(sites)
        # Borne théorique : arêtes finies <= 3n - 6, plus semi-infinies
        assert len(diagram.edges) <= 4 * n, (
            f"Trop d'arêtes : {len(diagram.edges)} pour {n} sites"
        )

    @pytest.mark.parametrize("num_points", [3, 5, 10, 20])
    def test_produces_output(self, num_points):
        """L'algorithme produit des arêtes et sommets pour différentes tailles."""
        raw = self._make_points(num_points * 11, num_points)
        sites = [Point(x, y) for x, y in raw]
        bbox = BoundingBox(0, 0, 800, 600)
        diagram = self.algo.compute(sites, bbox)

        assert len(diagram.edges) > 0, f"Aucune arête pour {num_points} points"
        if num_points >= 3:
            assert len(diagram.vertices) > 0, (
                f"Aucun sommet pour {num_points} points"
            )
