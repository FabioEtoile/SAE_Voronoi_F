import unittest
import numpy as np
from scipy.spatial import distance
from voronoi_core import VoronoiEngine

class TestVoronoiEngine(unittest.TestCase):
    def setUp(self):
        self.width = 800
        self.height = 600
        self.engine = VoronoiEngine(self.width, self.height)
        # Générer 50 points de tests aléatoires
        np.random.seed(42)
        self.points = [(float(x), float(y)) for x, y in np.random.rand(50, 2) * [self.width, self.height]]

    def test_voronoi_property(self):
        """
        Test unitaire crucial : 
        Vérifie que le centre géométrique (ou n'importe quel point) de la cellule calculée 
        est bien plus proche de son point générateur que de n'importe quel autre point.
        """
        cells = self.engine.compute_cells(self.points)
        
        # Vérifions qu'on a le bon nombre de cellules
        self.assertEqual(len(cells), len(self.points))
        
        for seed_point, poly in cells:
            if not poly or len(poly) < 3:
                continue # Ignorer les polygones dégénérés
            
            # Calculer le barycentre (centroid) du polygone
            x_coords = [p[0] for p in poly]
            y_coords = [p[1] for p in poly]
            centroid = (sum(x_coords)/len(poly), sum(y_coords)/len(poly))
            
            # Utiliser scipy (distance) pour vérifier la vérité terrain
            distances = distance.cdist([centroid], self.points)[0]
            closest_point_index = np.argmin(distances)
            closest_point = self.points[closest_point_index]
            
            # Le point le plus proche DU CENTRE DE LA CELLULE DOIT ETRE le seed_point
            # On utilise assertAlmostEqual pour pallier aux imprécisions flottantes minimes
            self.assertAlmostEqual(closest_point[0], seed_point[0], places=5)
            self.assertAlmostEqual(closest_point[1], seed_point[1], places=5)

    def test_bounding_box_limits(self):
        """Vérifie que les cellules ne sortent pas de l'image (boîte englobante)."""
        cells = self.engine.compute_cells(self.points)
        for _, poly in cells:
            for x, y in poly:
                self.assertTrue(0 - 1e-9 <= x <= self.width + 1e-9)
                self.assertTrue(0 - 1e-9 <= y <= self.height + 1e-9)

if __name__ == '__main__':
    unittest.main()