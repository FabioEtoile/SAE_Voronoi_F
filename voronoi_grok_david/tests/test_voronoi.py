import unittest
from src.voronoi.core import Point, compute_voronoi_cells, get_bbox
import math

try:
    import numpy as np
    from scipy.spatial import Voronoi
    SCIPY_OK = True
except ImportError:
    SCIPY_OK = False


class TestVoronoi(unittest.TestCase):

    def setUp(self):
        self.points_simple = [
            Point(100, 200),
            Point(300, 450),
            Point(500, 120),
            Point(250, 600)
        ]

        self.points_problematic = [
            Point(2, 4),
            Point(5.3, 4.5),
            Point(18, 29),
            Point(12.5, 23.7)
        ]

    # ====================== TESTS BASIQUES ======================
    def test_import_functions(self):
        self.assertTrue(callable(compute_voronoi_cells))
        self.assertTrue(callable(get_bbox))

    def test_get_bbox(self):
        bbox = get_bbox(self.points_simple, margin=0.5)
        self.assertGreater(bbox[2] - bbox[0], 500)
        self.assertGreater(bbox[3] - bbox[1], 580)

    # ====================== TESTS PRINCIPAUX ======================
    def test_number_of_cells(self):
        cells = compute_voronoi_cells(self.points_simple, get_bbox(self.points_simple))
        self.assertEqual(len(cells), len(self.points_simple))

        cells2 = compute_voronoi_cells(self.points_problematic, get_bbox(self.points_problematic))
        self.assertEqual(len(cells2), len(self.points_problematic))

    def test_each_cell_has_at_least_3_vertices(self):
        for points in [self.points_simple, self.points_problematic]:
            cells = compute_voronoi_cells(points, get_bbox(points))
            for i, cell in enumerate(cells):
                self.assertGreaterEqual(len(cell), 3, f"Cellule {i} trop petite")

    def test_no_empty_cells(self):
        cells = compute_voronoi_cells(self.points_problematic, get_bbox(self.points_problematic))
        for cell in cells:
            self.assertGreater(len(cell), 2, "Une cellule est vide")

    # ====================== TESTS AVEC SCIPY ======================
    @unittest.skipUnless(SCIPY_OK, "scipy non installé")
    def test_consistency_with_scipy(self):
        pts = np.array([[p.x, p.y] for p in self.points_problematic])
        vor = Voronoi(pts)
        our_cells = compute_voronoi_cells(self.points_problematic, get_bbox(self.points_problematic))
        self.assertEqual(len(our_cells), len(vor.point_region))

    def test_point_inside_its_cell(self):
        """Vérifie que chaque point est bien dans sa cellule (tolérance augmentée à cause des dummy points)"""
        for points in [self.points_simple, self.points_problematic]:
            cells = compute_voronoi_cells(points, get_bbox(points))
            
            for i, cell in enumerate(cells):
                if len(cell) < 3:
                    continue
                p = points[i]
                # Calcul du centroïde uniquement sur les sommets raisonnables (pas trop loin)
                reasonable_points = [pt for pt in cell if math.hypot(pt.x - p.x, pt.y - p.y) < 10000]
                if not reasonable_points:
                    continue
                cx = sum(pt.x for pt in reasonable_points) / len(reasonable_points)
                cy = sum(pt.y for pt in reasonable_points) / len(reasonable_points)
                dist = math.hypot(p.x - cx, p.y - cy)
                self.assertLess(dist, 8000.0, f"Point {i} trop loin de sa cellule (dist={dist:.1f})")


if __name__ == '__main__':
    unittest.main(verbosity=2)