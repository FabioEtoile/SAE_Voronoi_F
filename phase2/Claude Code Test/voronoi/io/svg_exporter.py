"""Export du diagramme de Voronoi en SVG via svgwrite."""

import colorsys
from pathlib import Path

import svgwrite

from voronoi.core.geometry import Point, Edge
from voronoi.core.voronoi_result import VoronoiDiagram


class SvgExporter:
    """Exporte un diagramme de Voronoi sous forme de fichier SVG."""

    PALETTE: list[str] = [
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B6",
        "#D55E00",
        "#CC79A7",
        "#9467BD",
        "#8C564B",
        "#7F7F7F",
    ]

    def export(
        self,
        diagram: VoronoiDiagram,
        output_path: Path,
        width: int = 800,
        height: int = 600,
        draw_sites: bool = True,
    ) -> None:
        """Rend le diagramme dans un fichier SVG."""
        dwg = svgwrite.Drawing(
            str(output_path),
            size=(f"{width}px", f"{height}px"),
            viewBox=f"0 0 {width} {height}",
        )

        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill="#FAFAFA"))

        if diagram.regions:
            self._draw_regions(dwg, diagram)

        if diagram.edges:
            self._draw_edges(dwg, diagram.edges)

        if draw_sites:
            self._draw_sites(dwg, diagram.sites)

        dwg.save()

    def _draw_regions(self, dwg: svgwrite.Drawing, diagram: VoronoiDiagram) -> None:
        """Dessine les régions de Voronoi comme des polygones remplis."""
        for site_idx, polygon_points in diagram.regions.items():
            if len(polygon_points) < 3:
                continue

            points = [(p.x, p.y) for p in polygon_points]
            color = self._get_color(site_idx)
            dwg.add(
                dwg.polygon(
                    points=points,
                    fill=color,
                    fill_opacity=0.6,
                    stroke="none",
                )
            )

    def _draw_edges(self, dwg: svgwrite.Drawing, edges: list[Edge]) -> None:
        """Dessine les arêtes de Voronoi comme des lignes SVG."""
        for edge in edges:
            dwg.add(
                dwg.line(
                    start=(edge.start.x, edge.start.y),
                    end=(edge.end.x, edge.end.y),
                    stroke="#2C3E50",
                    stroke_width=1.5,
                    stroke_linecap="round",
                )
            )

    def _draw_sites(self, dwg: svgwrite.Drawing, sites: list[Point]) -> None:
        """Dessine les sites comme des cercles SVG."""
        for site in sites:
            dwg.add(
                dwg.circle(
                    center=(site.x, site.y),
                    r=4,
                    fill="#141414",
                    stroke="white",
                    stroke_width=1,
                )
            )

    def _get_color(self, index: int) -> str:
        """Retourne une couleur déterministe pour l'index donné."""
        if index < len(self.PALETTE):
            return self.PALETTE[index]

        hue = (index * 0.618033988749895) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.90)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
