"""Lecture de fichiers de coordonnées .txt."""

from pathlib import Path

from voronoi.core.geometry import Point


class PointFileReader:
    """Lit les coordonnées de sites depuis des fichiers texte."""

    @staticmethod
    def read(file_path: Path) -> list[Point]:
        """
        Parse un fichier .txt avec 'x,y' par ligne.

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
            ValueError: Si une ligne ne peut pas être parsée.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {path}")

        points: list[Point] = []
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped:
                    continue

                parts = stripped.split(",")
                if len(parts) != 2:
                    raise ValueError(
                        f"Ligne {line_num} invalide : '{stripped}' "
                        f"(format attendu : x,y)"
                    )

                try:
                    x = float(parts[0].strip())
                    y = float(parts[1].strip())
                except ValueError:
                    raise ValueError(
                        f"Ligne {line_num} : coordonnées non numériques "
                        f"dans '{stripped}'"
                    )

                points.append(Point(x, y))

        return points

    @staticmethod
    def validate_points(
        points: list[Point], width: float, height: float
    ) -> list[Point]:
        """Filtre les points pour ne garder que ceux dans les dimensions données."""
        return [
            p for p in points
            if 0 <= p.x <= width and 0 <= p.y <= height
        ]
