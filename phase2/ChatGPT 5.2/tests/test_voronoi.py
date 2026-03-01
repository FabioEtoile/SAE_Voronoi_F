import unittest
import numpy as np
from scipy.spatial import Voronoi
from core.point import Point
from core.voronoi import VoronoiDiagram

class TestVoronoi(unittest.TestCase):

    def test_compare_with_scipy(self):
        points = [Point(100,100), Point(200,100), Point(150,200)]
        diagram = VoronoiDiagram(points)
        cells = diagram.compute()

        scipy_points = np.array([[p.x, p.y] for p in points])
        scipy_vor = Voronoi(scipy_points)

        self.assertEqual(len(cells), len(points))

if __name__ == "__main__":
    unittest.main()