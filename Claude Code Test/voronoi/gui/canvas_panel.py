"""Panneau de dessin avec affichage du diagramme de Voronoi et interaction souris."""

from __future__ import annotations

import colorsys
import os
import tempfile
import tkinter as tk
from typing import Callable, Optional

from voronoi.core.geometry import Point
from voronoi.core.voronoi_result import VoronoiDiagram


class CanvasPanel(tk.Frame):
    """Zone de dessin interactive pour le diagramme de Voronoi."""

    CANVAS_WIDTH: int = 800
    CANVAS_HEIGHT: int = 600
    SITE_RADIUS: int = 5
    EDGE_COLOR: str = "#2C3E50"
    BACKGROUND: str = "#FAFAFA"
    CLICK_THRESHOLD: float = 15.0

    PALETTE: list[str] = [
        "#E69F00", "#56B4E9", "#009E73", "#F0E442",
        "#0072B6", "#D55E00", "#CC79A7", "#9467BD",
        "#8C564B", "#7F7F7F",
    ]

    def __init__(
        self,
        parent: tk.Widget,
        on_point_added: Callable[[Point], None],
        on_point_removed: Callable[[Point], None],
    ) -> None:
        super().__init__(parent, bg="#ECEFF1")

        self._on_point_added = on_point_added
        self._on_point_removed = on_point_removed
        self._photo_image: Optional[tk.PhotoImage] = None

        self._canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.BACKGROUND,
            highlightthickness=1,
            highlightbackground="#BDC3C7",
            cursor="crosshair",
        )
        self._canvas.pack(padx=10, pady=10)

        self._canvas.bind("<Button-1>", self._on_left_click)
        self._canvas.bind("<Button-2>", self._on_right_click)
        self._canvas.bind("<Button-3>", self._on_right_click)

        self._sites: list[Point] = []

        hint = tk.Label(
            self,
            text="Clic gauche : ajouter un point  |  Clic droit : supprimer le plus proche",
            font=("Helvetica", 10),
            bg="#ECEFF1",
            fg="#7F8C8D",
        )
        hint.pack(pady=(0, 5))

    def set_sites(self, sites: list[Point]) -> None:
        """Met à jour la liste de sites interne."""
        self._sites = list(sites)

    def render_diagram(self, diagram: VoronoiDiagram) -> None:
        """Redessine le diagramme complet sur le canvas."""
        self._canvas.delete("all")

        if diagram.pixel_assignments:
            self._draw_regions_ppm(diagram)

        self._draw_edges_from_pixels(diagram)
        self._draw_sites(diagram.sites)

    def _draw_regions_ppm(self, diagram: VoronoiDiagram) -> None:
        """Dessine les régions colorées via une image PPM construite en mémoire."""
        if not diagram.pixel_assignments:
            return

        w = diagram.width
        h = diagram.height

        color_cache: dict[int, str] = {}
        for py in range(h):
            for px in range(w):
                idx = diagram.pixel_assignments[py][px]
                if idx not in color_cache:
                    color_cache[idx] = self._get_color_rgb(idx)

        header = f"P6\n{w} {h}\n255\n".encode("ascii")
        pixels = bytearray(w * h * 3)

        for py in range(h):
            row = diagram.pixel_assignments[py]
            for px in range(w):
                idx = row[px]
                r, g, b = color_cache[idx]
                offset = (py * w + px) * 3
                pixels[offset] = r
                pixels[offset + 1] = g
                pixels[offset + 2] = b

        fd, tmp_path = tempfile.mkstemp(suffix=".ppm")
        try:
            os.write(fd, header + bytes(pixels))
            os.close(fd)
            self._photo_image = tk.PhotoImage(file=tmp_path)
        finally:
            os.unlink(tmp_path)
        self._canvas.create_image(0, 0, anchor=tk.NW, image=self._photo_image)

    def _draw_edges_from_pixels(self, diagram: VoronoiDiagram) -> None:
        """Dessine les arêtes comme des lignes sur le canvas (pour Fortune)."""
        if not diagram.edges:
            return

        if diagram.pixel_assignments:
            return

        for edge in diagram.edges:
            self._canvas.create_line(
                edge.start.x, edge.start.y,
                edge.end.x, edge.end.y,
                fill=self.EDGE_COLOR,
                width=1.5,
            )

    def _draw_sites(self, sites: list[Point]) -> None:
        """Dessine les sites comme des cercles."""
        r = self.SITE_RADIUS
        for site in sites:
            self._canvas.create_oval(
                site.x - r, site.y - r,
                site.x + r, site.y + r,
                fill="#141414",
                outline="white",
                width=1,
            )

    def _on_left_click(self, event: tk.Event) -> None:
        """Ajoute un point à la position cliquée."""
        x = max(0, min(event.x, self.CANVAS_WIDTH - 1))
        y = max(0, min(event.y, self.CANVAS_HEIGHT - 1))
        point = Point(float(x), float(y))
        self._on_point_added(point)

    def _on_right_click(self, event: tk.Event) -> None:
        """Supprime le point le plus proche si dans le seuil."""
        if not self._sites:
            return

        click = Point(float(event.x), float(event.y))
        min_dist = float("inf")
        nearest: Optional[Point] = None

        for site in self._sites:
            d = click.distance_to(site)
            if d < min_dist:
                min_dist = d
                nearest = site

        if nearest and min_dist <= self.CLICK_THRESHOLD:
            self._on_point_removed(nearest)

    def _get_color_rgb(self, index: int) -> tuple[int, int, int]:
        """Retourne un triplet RGB pour l'index donné."""
        hex_colors = self.PALETTE
        if index < len(hex_colors):
            h = hex_colors[index].lstrip("#")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

        hue = (index * 0.618033988749895) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.90)
        return (int(r * 255), int(g * 255), int(b * 255))
