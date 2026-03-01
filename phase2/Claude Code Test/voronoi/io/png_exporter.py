"""Export du diagramme de Voronoi en PNG via Pillow."""

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw

from voronoi.core.geometry import Point
from voronoi.core.voronoi_result import VoronoiDiagram


class PngExporter:
    """Exporte un diagramme de Voronoi sous forme d'image PNG."""

    PALETTE: list[tuple[int, int, int]] = [
        (230, 159, 0),
        (86, 180, 233),
        (0, 158, 115),
        (240, 228, 66),
        (0, 114, 178),
        (213, 94, 0),
        (204, 121, 167),
        (148, 103, 189),
        (140, 86, 75),
        (127, 127, 127),
    ]

    def export(
        self,
        diagram: VoronoiDiagram,
        output_path: Path,
        draw_sites: bool = True,
        draw_edges: bool = True,
    ) -> None:
        """Rend le diagramme dans un fichier PNG."""
        width = diagram.width
        height = diagram.height

        img = Image.new("RGB", (width, height), (255, 255, 255))

        if diagram.pixel_assignments:
            self._render_regions(img, diagram)

        draw = ImageDraw.Draw(img)

        if draw_edges and diagram.pixel_assignments:
            self._render_edge_pixels(img, diagram)

        if draw_sites:
            self._render_sites(draw, diagram.sites, diagram)

        img.save(str(output_path), "PNG")

    def _render_regions(self, img: Image.Image, diagram: VoronoiDiagram) -> None:
        """Colore chaque pixel selon sa région."""
        if not diagram.pixel_assignments:
            return

        pixels = img.load()
        for py in range(diagram.height):
            for px in range(diagram.width):
                site_idx = diagram.pixel_assignments[py][px]
                color = self._get_color(site_idx)
                pixels[px, py] = color

    def _render_edge_pixels(self, img: Image.Image, diagram: VoronoiDiagram) -> None:
        """Dessine les pixels frontières en noir."""
        if not diagram.pixel_assignments:
            return

        pixels = img.load()
        assignments = diagram.pixel_assignments
        w, h = diagram.width, diagram.height

        for py in range(h):
            for px in range(w):
                current = assignments[py][px]
                is_edge = False
                if px + 1 < w and assignments[py][px + 1] != current:
                    is_edge = True
                elif py + 1 < h and assignments[py + 1][px] != current:
                    is_edge = True
                elif px - 1 >= 0 and assignments[py][px - 1] != current:
                    is_edge = True
                elif py - 1 >= 0 and assignments[py - 1][px] != current:
                    is_edge = True

                if is_edge:
                    pixels[px, py] = (44, 62, 80)

    def _render_sites(
        self, draw: ImageDraw.Draw, sites: list[Point], diagram: VoronoiDiagram
    ) -> None:
        """Dessine les sites comme des cercles pleins."""
        radius = 4
        for site in sites:
            sx = site.x - diagram.sites[0].x + site.x if False else site.x
            sx = site.x
            sy = site.y
            draw.ellipse(
                [sx - radius, sy - radius, sx + radius, sy + radius],
                fill=(20, 20, 20),
                outline=(255, 255, 255),
                width=1,
            )

    def _get_color(self, index: int) -> tuple[int, int, int]:
        """Retourne une couleur déterministe pour l'index donné."""
        if index < len(self.PALETTE):
            return self.PALETTE[index]

        hue = (index * 0.618033988749895) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.90)
        return (int(r * 255), int(g * 255), int(b * 255))
