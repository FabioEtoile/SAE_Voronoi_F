"""Tests pour le lecteur de fichiers de coordonnées."""

import pytest
from pathlib import Path
import tempfile
import os

from voronoi.core.geometry import Point
from voronoi.io.reader import PointFileReader


class TestPointFileReader:
    def test_read_valid_file(self, tmp_path):
        """Lecture d'un fichier valide."""
        f = tmp_path / "valid.txt"
        f.write_text("100,200\n300,400\n500,600\n")

        points = PointFileReader.read(f)
        assert len(points) == 3
        assert points[0] == Point(100, 200)
        assert points[1] == Point(300, 400)
        assert points[2] == Point(500, 600)

    def test_read_with_spaces(self, tmp_path):
        """Lecture avec espaces autour des virgules."""
        f = tmp_path / "spaces.txt"
        f.write_text("100 , 200\n 300, 400 \n")

        points = PointFileReader.read(f)
        assert len(points) == 2
        assert points[0] == Point(100, 200)

    def test_read_empty_lines_skipped(self, tmp_path):
        """Les lignes vides sont ignorées."""
        f = tmp_path / "empty_lines.txt"
        f.write_text("100,200\n\n300,400\n\n")

        points = PointFileReader.read(f)
        assert len(points) == 2

    def test_read_empty_file(self, tmp_path):
        """Un fichier vide retourne une liste vide."""
        f = tmp_path / "empty.txt"
        f.write_text("")

        points = PointFileReader.read(f)
        assert points == []

    def test_read_file_not_found(self):
        """Fichier inexistant lève FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            PointFileReader.read(Path("/nonexistent/file.txt"))

    def test_read_malformed_line(self, tmp_path):
        """Ligne malformée lève ValueError."""
        f = tmp_path / "malformed.txt"
        f.write_text("100,200\nabc\n300,400\n")

        with pytest.raises(ValueError, match="invalide"):
            PointFileReader.read(f)

    def test_read_non_numeric(self, tmp_path):
        """Coordonnées non numériques lève ValueError."""
        f = tmp_path / "non_numeric.txt"
        f.write_text("abc,def\n")

        with pytest.raises(ValueError, match="non numériques"):
            PointFileReader.read(f)

    def test_read_float_coordinates(self, tmp_path):
        """Coordonnées à virgule flottante."""
        f = tmp_path / "floats.txt"
        f.write_text("100.5,200.7\n300.3,400.9\n")

        points = PointFileReader.read(f)
        assert len(points) == 2
        assert points[0] == Point(100.5, 200.7)

    def test_read_sample_format(self, tmp_path):
        """Format identique aux données d'exemple."""
        f = tmp_path / "sample.txt"
        f.write_text("213,247\n54,424\n180,29\n212,237\n50,370\n95,26\n162,300\n485,174\n")

        points = PointFileReader.read(f)
        assert len(points) == 8
        assert points[0] == Point(213, 247)
        assert points[7] == Point(485, 174)

    def test_validate_points_all_inside(self):
        """Tous les points dans les limites."""
        points = [Point(100, 200), Point(500, 400)]
        result = PointFileReader.validate_points(points, 800, 600)
        assert len(result) == 2

    def test_validate_points_some_outside(self):
        """Certains points hors limites sont filtrés."""
        points = [Point(100, 200), Point(900, 400), Point(-10, 300)]
        result = PointFileReader.validate_points(points, 800, 600)
        assert len(result) == 1
        assert result[0] == Point(100, 200)
