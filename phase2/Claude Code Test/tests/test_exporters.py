"""Tests pour les exporteurs PNG et SVG."""

import pytest
from pathlib import Path

from voronoi.core.geometry import Point, BoundingBox
from voronoi.core.brute_force import BruteForceVoronoi
from voronoi.core.fortune import FortuneVoronoi
from voronoi.core.voronoi_result import VoronoiDiagram
from voronoi.io.png_exporter import PngExporter
from voronoi.io.svg_exporter import SvgExporter


class TestPngExporter:
    def setup_method(self):
        self.exporter = PngExporter()
        self.algo = BruteForceVoronoi()

    def test_export_creates_file(self, tmp_path):
        """L'export crée bien un fichier PNG."""
        bbox = BoundingBox(0, 0, 200, 150)
        sites = [Point(50, 75), Point(150, 75)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.png"
        self.exporter.export(diagram, out)

        assert out.exists()
        assert out.stat().st_size > 0

    def test_export_correct_dimensions(self, tmp_path):
        """L'image PNG a les bonnes dimensions."""
        from PIL import Image

        bbox = BoundingBox(0, 0, 300, 200)
        sites = [Point(100, 100), Point(200, 100)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.png"
        self.exporter.export(diagram, out)

        img = Image.open(out)
        assert img.size == (300, 200)

    def test_export_without_sites(self, tmp_path):
        """Export sans dessiner les sites."""
        bbox = BoundingBox(0, 0, 200, 150)
        sites = [Point(50, 75), Point(150, 75)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.png"
        self.exporter.export(diagram, out, draw_sites=False)

        assert out.exists()

    def test_color_palette(self):
        """La palette de couleurs est bien définie."""
        exporter = PngExporter()
        for i in range(20):
            color = exporter._get_color(i)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)


class TestSvgExporter:
    def setup_method(self):
        self.exporter = SvgExporter()
        self.algo = FortuneVoronoi()

    def test_export_creates_file(self, tmp_path):
        """L'export crée bien un fichier SVG."""
        bbox = BoundingBox(0, 0, 200, 150)
        sites = [Point(50, 75), Point(150, 75)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.svg"
        self.exporter.export(diagram, out, width=200, height=150)

        assert out.exists()
        assert out.stat().st_size > 0

    def test_svg_contains_expected_elements(self, tmp_path):
        """Le SVG contient les éléments attendus."""
        bbox = BoundingBox(0, 0, 400, 300)
        sites = [Point(100, 150), Point(300, 150)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.svg"
        self.exporter.export(diagram, out, width=400, height=300)

        content = out.read_text()
        assert "<svg" in content
        assert "<circle" in content  # sites
        assert "<line" in content or "<rect" in content  # edges or background

    def test_svg_without_sites(self, tmp_path):
        """Export SVG sans les marqueurs de sites."""
        bbox = BoundingBox(0, 0, 200, 150)
        sites = [Point(50, 75), Point(150, 75)]
        diagram = self.algo.compute(sites, bbox)

        out = tmp_path / "test.svg"
        self.exporter.export(diagram, out, width=200, height=150, draw_sites=False)

        content = out.read_text()
        assert "<circle" not in content

    def test_color_palette(self):
        """La palette SVG est bien définie."""
        exporter = SvgExporter()
        for i in range(20):
            color = exporter._get_color(i)
            assert color.startswith("#")
            assert len(color) == 7
