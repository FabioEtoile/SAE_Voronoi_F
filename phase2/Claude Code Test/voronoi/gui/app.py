"""Application principale du générateur de diagrammes de Voronoi."""

from __future__ import annotations

import time
import tkinter as tk
from pathlib import Path

from voronoi.core.geometry import Point, BoundingBox
from voronoi.core.brute_force import BruteForceVoronoi
from voronoi.core.fortune import FortuneVoronoi
from voronoi.core.voronoi_result import VoronoiDiagram
from voronoi.gui.canvas_panel import CanvasPanel
from voronoi.gui.control_panel import ControlPanel
from voronoi.gui.dialogs import show_error, show_info
from voronoi.io.reader import PointFileReader
from voronoi.io.png_exporter import PngExporter
from voronoi.io.svg_exporter import SvgExporter


class VoronoiApp:
    """Fenêtre principale de l'application Voronoi."""

    WINDOW_TITLE: str = "Voronoi Diagram Generator"
    MIN_WIDTH: int = 1120
    MIN_HEIGHT: int = 700

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._sites: list[Point] = []
        self._current_diagram: VoronoiDiagram | None = None

        self._brute_force = BruteForceVoronoi()
        self._fortune = FortuneVoronoi()
        self._png_exporter = PngExporter()
        self._svg_exporter = SvgExporter()

        self._canvas_panel: CanvasPanel | None = None
        self._control_panel: ControlPanel | None = None

    def run(self) -> None:
        """Initialise les widgets et démarre la boucle principale."""
        self._setup_window()
        self._setup_layout()
        self._root.mainloop()

    def _setup_window(self) -> None:
        """Configure la fenêtre principale."""
        self._root.title(self.WINDOW_TITLE)
        self._root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self._root.configure(bg="#F5F6FA")

        try:
            self._root.tk.call("tk", "scaling", 1.0)
        except tk.TclError:
            pass

    def _setup_layout(self) -> None:
        """Crée le layout deux panneaux."""
        main_frame = tk.Frame(self._root, bg="#F5F6FA")
        main_frame.pack(fill="both", expand=True)

        self._canvas_panel = CanvasPanel(
            main_frame,
            on_point_added=self._on_point_added,
            on_point_removed=self._on_point_removed,
        )
        self._canvas_panel.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        self._control_panel = ControlPanel(
            main_frame,
            on_load=self._on_load_file,
            on_export=self._on_export,
            on_clear=self._on_clear,
            on_remove_point=self._on_remove_point_by_index,
        )
        self._control_panel.pack(side="right", fill="y", padx=10, pady=10)

        self._status_var = tk.StringVar(value="Prêt")
        status_bar = tk.Label(
            self._root,
            textvariable=self._status_var,
            font=("Helvetica", 9),
            bg="#ECEFF1",
            fg="#7F8C8D",
            anchor="w",
            padx=10,
            pady=4,
        )
        status_bar.pack(fill="x", side="bottom")

    def _on_point_added(self, point: Point) -> None:
        """Appelé quand un point est ajouté via clic."""
        self._sites.append(point)
        self._refresh()

    def _on_point_removed(self, point: Point) -> None:
        """Appelé quand un point est supprimé via clic droit."""
        self._sites = [
            s for s in self._sites
            if not (abs(s.x - point.x) < 1e-6 and abs(s.y - point.y) < 1e-6)
        ]
        self._refresh()

    def _on_remove_point_by_index(self, index: int) -> None:
        """Supprime un point par son index dans la liste."""
        if 0 <= index < len(self._sites):
            self._sites.pop(index)
            self._refresh()

    def _on_load_file(self, path: Path) -> None:
        """Charge les points depuis un fichier."""
        try:
            points = PointFileReader.read(path)
            if not points:
                show_error(self._root, "Erreur", "Le fichier ne contient aucun point.")
                return

            self._sites = points
            self._status_var.set(f"{len(points)} points chargés depuis {path.name}")
            self._refresh()
        except (FileNotFoundError, ValueError) as e:
            show_error(self._root, "Erreur de lecture", str(e))

    def _on_export(self, fmt: str, path: Path) -> None:
        """Exporte le diagramme dans le format choisi."""
        if len(self._sites) < 2:
            show_error(
                self._root,
                "Export impossible",
                "Il faut au moins 2 points pour exporter.",
            )
            return

        try:
            bbox = BoundingBox(
                0, 0,
                CanvasPanel.CANVAS_WIDTH,
                CanvasPanel.CANVAS_HEIGHT,
            )

            if fmt == "PNG":
                diagram = self._brute_force.compute(self._sites, bbox)
                self._png_exporter.export(diagram, path)
            else:
                diagram = self._fortune.compute(self._sites, bbox)
                self._svg_exporter.export(
                    diagram, path,
                    width=CanvasPanel.CANVAS_WIDTH,
                    height=CanvasPanel.CANVAS_HEIGHT,
                )

            show_info(
                self._root,
                "Export réussi",
                f"Diagramme exporté vers :\n{path}",
            )
            self._status_var.set(f"Exporté : {path.name}")
        except Exception as e:
            show_error(self._root, "Erreur d'export", str(e))

    def _on_clear(self) -> None:
        """Efface tous les points."""
        self._sites.clear()
        self._current_diagram = None
        self._refresh()
        self._status_var.set("Canvas effacé")

    def _refresh(self) -> None:
        """Recalcule et redessine le diagramme."""
        if self._canvas_panel:
            self._canvas_panel.set_sites(self._sites)

        if self._control_panel:
            self._control_panel.update_point_count(len(self._sites))
            self._control_panel.update_points_list(self._sites)

        if len(self._sites) < 2:
            if self._canvas_panel:
                empty = VoronoiDiagram(
                    sites=self._sites,
                    width=CanvasPanel.CANVAS_WIDTH,
                    height=CanvasPanel.CANVAS_HEIGHT,
                )
                self._canvas_panel.render_diagram(empty)
            if self._control_panel:
                self._control_panel.update_computation_time(0.0)
            return

        bbox = BoundingBox(
            0, 0,
            CanvasPanel.CANVAS_WIDTH,
            CanvasPanel.CANVAS_HEIGHT,
        )

        start = time.perf_counter()
        self._current_diagram = self._brute_force.compute(self._sites, bbox)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if self._canvas_panel:
            self._canvas_panel.render_diagram(self._current_diagram)

        if self._control_panel:
            self._control_panel.update_computation_time(elapsed_ms)

        self._status_var.set(f"{len(self._sites)} points | Calcul : {elapsed_ms:.1f} ms")
