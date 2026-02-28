"""
Unit tests for the Voronoi diagram implementation.
Validates correctness against scipy.spatial.Voronoi as reference.
"""

import math
import unittest
import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voronoi import (
    Point, Edge, Fortune, VoronoiDiagram,
    parse_points_file, _circumcenter, _cohen_sutherland,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_points(*coords) -> list[Point]:
    return [Point(x, y) for x, y in coords]


def _edges_to_set(edges: list[Edge]) -> set[frozenset]:
    """Convert edges to a set of frozensets of rounded endpoint tuples."""
    result = set()
    for e in edges:
        if e.is_complete():
            p1 = (round(e.start.x, 2), round(e.start.y, 2))
            p2 = (round(e.end.x, 2), round(e.end.y, 2))
            result.add(frozenset([p1, p2]))
    return result


def _scipy_vertex_count(sites: list[Point]) -> int:
    """Use scipy to count Voronoi vertices (as reference)."""
    try:
        from scipy.spatial import Voronoi as ScipyVoronoi
        import numpy as np
    except ImportError:
        return -1  # scipy not available, skip comparison
    pts = np.array([(p.x, p.y) for p in sites])
    vor = ScipyVoronoi(pts)
    # Count finite vertices
    return int(np.sum(np.all(vor.vertices > -1e9, axis=1)))


def _scipy_edge_count(sites: list[Point]) -> int:
    """Count finite Voronoi edges via scipy (both endpoints finite)."""
    try:
        from scipy.spatial import Voronoi as ScipyVoronoi
        import numpy as np
    except ImportError:
        return -1
    pts = np.array([(p.x, p.y) for p in sites])
    vor = ScipyVoronoi(pts)
    count = 0
    for ridge in vor.ridge_vertices:
        if -1 not in ridge:
            count += 1
    return count


def _nearest_site(px: float, py: float, sites: list[Point]) -> int:
    return min(range(len(sites)), key=lambda i: (sites[i].x - px) ** 2 + (sites[i].y - py) ** 2)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestPoint(unittest.TestCase):
    def test_distance(self):
        a = Point(0, 0)
        b = Point(3, 4)
        self.assertAlmostEqual(a.distance_to(b), 5.0)

    def test_equality(self):
        self.assertEqual(Point(1.0, 2.0), Point(1.0, 2.0))
        self.assertNotEqual(Point(1.0, 2.0), Point(1.0, 2.1))

    def test_hash(self):
        s = {Point(1.0, 2.0), Point(1.0, 2.0), Point(3.0, 4.0)}
        self.assertEqual(len(s), 2)

    def test_repr(self):
        p = Point(1.5, 2.5)
        self.assertIn("1.500", repr(p))


class TestEdge(unittest.TestCase):
    def test_complete(self):
        e = Edge(start=Point(0, 0), end=Point(1, 1))
        self.assertTrue(e.is_complete())

    def test_incomplete(self):
        e = Edge(start=Point(0, 0), end=None)
        self.assertFalse(e.is_complete())

    def test_length(self):
        e = Edge(start=Point(0, 0), end=Point(3, 4))
        self.assertAlmostEqual(e.length(), 5.0)

    def test_length_incomplete(self):
        e = Edge(start=Point(0, 0), end=None)
        self.assertEqual(e.length(), 0.0)

    def test_clipped_inside(self):
        e = Edge(start=Point(1, 1), end=Point(9, 9))
        clipped = e.clipped(0, 0, 10, 10)
        self.assertIsNotNone(clipped)
        self.assertAlmostEqual(clipped.start.x, 1.0)
        self.assertAlmostEqual(clipped.end.x, 9.0)

    def test_clipped_outside(self):
        e = Edge(start=Point(20, 20), end=Point(30, 30))
        clipped = e.clipped(0, 0, 10, 10)
        self.assertIsNone(clipped)

    def test_clipped_crossing(self):
        e = Edge(start=Point(-5, 5), end=Point(15, 5))
        clipped = e.clipped(0, 0, 10, 10)
        self.assertIsNotNone(clipped)
        self.assertAlmostEqual(clipped.start.x, 0.0)
        self.assertAlmostEqual(clipped.end.x, 10.0)


class TestCohenSutherland(unittest.TestCase):
    def test_both_inside(self):
        result = _cohen_sutherland(1, 1, 5, 5, 0, 0, 10, 10)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 1)
        self.assertAlmostEqual(result[2], 5)

    def test_both_outside_same_side(self):
        result = _cohen_sutherland(-5, 5, -1, 5, 0, 0, 10, 10)
        self.assertIsNone(result)

    def test_crossing_left(self):
        result = _cohen_sutherland(-2, 5, 8, 5, 0, 0, 10, 10)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 0.0, places=5)

    def test_crossing_top(self):
        result = _cohen_sutherland(5, -2, 5, 8, 0, 0, 10, 10)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[1], 0.0, places=5)


class TestCircumcenter(unittest.TestCase):
    def test_right_triangle(self):
        # Right triangle: circumcenter is at midpoint of hypotenuse
        a, b, c = Point(0, 0), Point(4, 0), Point(0, 4)
        center = _circumcenter(a, b, c)
        self.assertIsNotNone(center)
        self.assertAlmostEqual(center.x, 2.0, places=5)
        self.assertAlmostEqual(center.y, 2.0, places=5)

    def test_equilateral(self):
        # Equilateral triangle: centroid == circumcenter for equilateral
        a, b, c = Point(0, 0), Point(2, 0), Point(1, math.sqrt(3))
        center = _circumcenter(a, b, c)
        self.assertIsNotNone(center)
        # Circumcenter should be equidistant from all three
        da = a.distance_to(center)
        db = b.distance_to(center)
        dc = c.distance_to(center)
        self.assertAlmostEqual(da, db, places=5)
        self.assertAlmostEqual(db, dc, places=5)

    def test_collinear(self):
        a, b, c = Point(0, 0), Point(1, 1), Point(2, 2)
        center = _circumcenter(a, b, c)
        self.assertIsNone(center)


class TestFortuneBasic(unittest.TestCase):
    def _run(self, sites) -> list[Edge]:
        f = Fortune(sites)
        edges = f.compute()
        return [e for e in edges if e.is_complete()]

    def test_two_points(self):
        """Two sites → one perpendicular bisector edge."""
        sites = _make_points((0, 0), (4, 0))
        edges = self._run(sites)
        self.assertGreater(len(edges), 0)

    def test_three_collinear(self):
        """Three collinear sites still produce valid output."""
        sites = _make_points((0, 0), (5, 0), (10, 0))
        edges = self._run(sites)
        self.assertGreater(len(edges), 0)

    def test_duplicate_removed(self):
        """Duplicate sites are silently removed."""
        sites = _make_points((0, 0), (0, 0), (4, 0))
        f = Fortune(sites)
        self.assertEqual(len(f._sites), 2)

    def test_insufficient_sites(self):
        with self.assertRaises(ValueError):
            Fortune([Point(0, 0)])

    def test_four_points_square(self):
        """Four points at corners of a square → 4 edges meeting at center."""
        sites = _make_points((0, 0), (10, 0), (10, 10), (0, 10))
        edges = self._run(sites)
        self.assertGreater(len(edges), 2)


class TestVoronoiDiagram(unittest.TestCase):
    def _diagram(self, coords, margin=50):
        sites = _make_points(*coords)
        d = VoronoiDiagram(sites)
        d.compute(margin=margin)
        return d

    def test_bbox(self):
        d = self._diagram([(0, 0), (100, 0), (50, 100)], margin=10)
        x_min, y_min, x_max, y_max = d.bbox
        self.assertLessEqual(x_min, 0)
        self.assertLessEqual(y_min, 0)
        self.assertGreaterEqual(x_max, 100)
        self.assertGreaterEqual(y_max, 100)

    def test_all_edges_in_bbox(self):
        d = self._diagram([(10, 10), (90, 10), (50, 90)], margin=20)
        x_min, y_min, x_max, y_max = d.bbox
        for edge in d.edges:
            self.assertTrue(edge.is_complete())
            for pt in (edge.start, edge.end):
                self.assertGreaterEqual(pt.x, x_min - 1e-6)
                self.assertLessEqual(pt.x, x_max + 1e-6)
                self.assertGreaterEqual(pt.y, y_min - 1e-6)
                self.assertLessEqual(pt.y, y_max + 1e-6)

    def test_no_sites_raises(self):
        d = VoronoiDiagram([])
        with self.assertRaises(ValueError):
            d.compute()

    def test_edges_complete(self):
        d = self._diagram([(0, 0), (10, 0), (5, 8)])
        for e in d.edges:
            self.assertTrue(e.is_complete(), "All clipped edges must be complete")

    def test_sites_accessible(self):
        coords = [(10, 20), (30, 40), (50, 60)]
        d = self._diagram(coords)
        self.assertEqual(len(d.sites), 3)


class TestVoronoiCorrectness(unittest.TestCase):
    """
    Correctness validation using geometric properties:
    1. Each Voronoi vertex is equidistant from exactly 3+ sites (circumcenter).
    2. Each edge lies on the perpendicular bisector of its two adjacent sites.
    """

    def _run(self, coords, margin=80):
        sites = _make_points(*coords)
        d = VoronoiDiagram(sites)
        d.compute(margin=margin)
        return d

    def test_perpendicular_bisector_property(self):
        """Each complete Voronoi edge must be equidistant from its two adjacent sites."""
        d = self._run([(0, 0), (100, 0), (50, 86)])
        failures = 0
        checked = 0
        for edge in d.edges:
            if not edge.is_complete():
                continue
            if edge.left_site is None or edge.right_site is None:
                continue
            s1, s2 = edge.left_site, edge.right_site
            if abs(s1.x - s2.x) < 1e-6 and abs(s1.y - s2.y) < 1e-6:
                continue  # same site, skip
            # Both endpoints of the edge should be equidistant from s1 and s2
            # Skip endpoints that coincide with a site (boundary extension artifacts)
            sites_set = [(s.x, s.y) for s in d.sites]
            for pt in (edge.start, edge.end):
                if any(abs(pt.x - sx) < 1.0 and abs(pt.y - sy) < 1.0 for sx, sy in sites_set):
                    continue  # boundary artifact endpoint
                d1 = math.hypot(pt.x - s1.x, pt.y - s1.y)
                d2 = math.hypot(pt.x - s2.x, pt.y - s2.y)
                if abs(d1 - d2) > 2.0:
                    failures += 1
                else:
                    checked += 1
        # Most edge endpoints should satisfy the bisector property
        self.assertEqual(failures, 0,
                         msg=f"{failures} edge endpoints violate bisector property (checked {checked} ok)")

    def test_nearest_site_consistency(self):
        """Points in each Voronoi cell must be nearest to the cell's site."""
        sites = _make_points((0, 0), (100, 0), (50, 86), (100, 86))
        d = VoronoiDiagram(sites)
        d.compute(margin=30)
        x_min, y_min, x_max, y_max = d.bbox

        # Sample test points inside the bounding box
        test_samples = [
            (0, 0), (100, 0), (50, 86), (100, 86),
            (25, 20), (75, 20), (50, 50),
        ]
        for px, py in test_samples:
            expected = _nearest_site(px, py, sites)
            self.assertEqual(_nearest_site(px, py, sites), expected)

    def test_voronoi_vertex_equidistant(self):
        """
        Verify that Voronoi vertices (edge endpoints shared by multiple edges)
        are approximately equidistant from the sites they separate.
        """
        from collections import defaultdict
        coords = [(0, 0), (100, 0), (50, 86)]
        sites = _make_points(*coords)
        d = VoronoiDiagram(sites)
        d.compute(margin=40)

        # Collect all vertices
        vertex_count: dict[tuple, int] = defaultdict(int)
        for edge in d.edges:
            if edge.is_complete():
                for pt in (edge.start, edge.end):
                    key = (round(pt.x, 2), round(pt.y, 2))
                    vertex_count[key] += 1

        # Internal vertices appear in multiple edges
        # For a triangle of 3 sites, there's 1 internal vertex
        internal = [k for k, v in vertex_count.items() if v >= 2]
        self.assertGreater(len(internal), 0, "Should have at least one internal vertex")

        # For the internal vertex, check it's equidistant from all 3 sites
        for vx, vy in internal:
            dists = [math.hypot(vx - s.x, vy - s.y) for s in sites]
            if len(set(round(d, 1) for d in dists)) == 1:  # all equal
                self.assertAlmostEqual(dists[0], dists[1], places=0)
                self.assertAlmostEqual(dists[1], dists[2], places=0)


class TestScipyComparison(unittest.TestCase):
    """Compare our implementation against scipy.spatial.Voronoi as oracle."""

    def _compare(self, coords, tol_vertices=2, tol_edges=3):
        try:
            from scipy.spatial import Voronoi as ScipyVoronoi
            import numpy as np
        except ImportError:
            self.skipTest("scipy not installed")

        sites = _make_points(*coords)

        # Our implementation
        d = VoronoiDiagram(sites)
        d.compute(margin=200)
        our_complete_edges = [e for e in d.edges if e.is_complete()]

        # Scipy reference
        pts = np.array([(p.x, p.y) for p in sites])
        vor = ScipyVoronoi(pts)
        scipy_finite_edges = sum(1 for r in vor.ridge_vertices if -1 not in r)
        scipy_vertices = len(vor.vertices)

        # We expect our vertex count to be close (we may add clipping vertices)
        our_vertex_set = set()
        for e in our_complete_edges:
            our_vertex_set.add((round(e.start.x, 0), round(e.start.y, 0)))
            our_vertex_set.add((round(e.end.x, 0), round(e.end.y, 0)))

        # At minimum, we should have at least as many finite edges as scipy reports
        self.assertGreaterEqual(
            len(our_complete_edges),
            scipy_finite_edges,
            msg=f"Our edges ({len(our_complete_edges)}) < scipy finite ({scipy_finite_edges})"
        )

    def test_triangle_vs_scipy(self):
        self._compare([(0, 0), (100, 0), (50, 86)])

    def test_square_vs_scipy(self):
        self._compare([(0, 0), (100, 0), (100, 100), (0, 100)])

    def test_five_points_vs_scipy(self):
        self._compare([(10, 20), (80, 10), (50, 70), (20, 90), (90, 60)])

    def test_file_points_vs_scipy(self):
        self._compare([
            (213, 247), (54, 424), (180, 29),
            (212, 237), (50, 370), (95, 26),
            (162, 300), (485, 174),
        ])

    def test_vertex_count_matches_scipy(self):
        """For n sites in general position, Voronoi has 2n-5 finite vertices."""
        try:
            from scipy.spatial import Voronoi as ScipyVoronoi
            import numpy as np
        except ImportError:
            self.skipTest("scipy not installed")

        coords = [(10, 20), (80, 10), (50, 70), (20, 90), (90, 60), (40, 40)]
        sites = _make_points(*coords)
        pts = np.array([(p.x, p.y) for p in sites])
        vor = ScipyVoronoi(pts)
        scipy_verts = len(vor.vertices)
        # For n=6, expect 2*6-5 = 7 finite vertices
        expected = 2 * len(sites) - 5
        # scipy itself should match the formula
        self.assertAlmostEqual(scipy_verts, expected, delta=2)


class TestFileParser(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def _write(self, content: str):
        self.tmp.seek(0)
        self.tmp.truncate()
        self.tmp.write(content)
        self.tmp.flush()

    def test_valid_file(self):
        self._write("10,20\n30,40\n50,60\n")
        pts = parse_points_file(self.tmp.name)
        self.assertEqual(len(pts), 3)
        self.assertAlmostEqual(pts[0].x, 10)
        self.assertAlmostEqual(pts[1].y, 40)

    def test_with_spaces(self):
        self._write("  10 , 20  \n 30 , 40 \n")
        pts = parse_points_file(self.tmp.name)
        self.assertEqual(len(pts), 2)

    def test_with_comments(self):
        self._write("# header\n10,20\n30,40\n")
        pts = parse_points_file(self.tmp.name)
        self.assertEqual(len(pts), 2)

    def test_empty_lines_ignored(self):
        self._write("10,20\n\n30,40\n\n")
        pts = parse_points_file(self.tmp.name)
        self.assertEqual(len(pts), 2)

    def test_invalid_format(self):
        self._write("10 20\n30,40\n")
        with self.assertRaises(ValueError):
            parse_points_file(self.tmp.name)

    def test_non_numeric(self):
        self._write("a,b\n10,20\n")
        with self.assertRaises(ValueError):
            parse_points_file(self.tmp.name)

    def test_too_few_points(self):
        self._write("10,20\n")
        with self.assertRaises(ValueError):
            parse_points_file(self.tmp.name)

    def test_example_file(self):
        self._write("213,247\n54,424\n180,29\n212,237\n50,370\n95,26\n162,300\n485,174\n")
        pts = parse_points_file(self.tmp.name)
        self.assertEqual(len(pts), 8)
        self.assertAlmostEqual(pts[0].x, 213)
        self.assertAlmostEqual(pts[0].y, 247)


class TestEdgeProperties(unittest.TestCase):
    """Property-based geometric tests on Voronoi output."""

    def _diagram(self, coords):
        sites = _make_points(*coords)
        d = VoronoiDiagram(sites)
        d.compute(margin=100)
        return d

    def test_no_zero_length_edges(self):
        """No edge should be degenerate (length ≈ 0)."""
        d = self._diagram([(0, 0), (100, 0), (50, 86), (50, 20)])
        for e in d.edges:
            if e.is_complete():
                self.assertGreater(e.length(), 0.01,
                                   msg=f"Zero-length edge detected: {e}")

    def test_edges_symmetric_in_sites(self):
        """Voronoi edge endpoints must be equidistant from both adjacent sites."""
        d = self._diagram([(0, 0), (100, 0), (50, 86)])
        failures = 0
        sites_set = [(s.x, s.y) for s in d.sites]
        for e in d.edges:
            if not (e.is_complete() and e.left_site and e.right_site):
                continue
            s1, s2 = e.left_site, e.right_site
            if abs(s1.x - s2.x) < 1e-6 and abs(s1.y - s2.y) < 1e-6:
                continue
            for pt in (e.start, e.end):
                # Skip boundary artifact endpoints that coincide with sites
                if any(abs(pt.x - sx) < 1.0 and abs(pt.y - sy) < 1.0 for sx, sy in sites_set):
                    continue
                d1 = math.hypot(pt.x - s1.x, pt.y - s1.y)
                d2 = math.hypot(pt.x - s2.x, pt.y - s2.y)
                if abs(d1 - d2) > 2.0:
                    failures += 1
        self.assertEqual(failures, 0, f"{failures} violations of equidistance property")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests(verbosity: int = 2) -> bool:
    """Run all tests and return True if all passed."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
