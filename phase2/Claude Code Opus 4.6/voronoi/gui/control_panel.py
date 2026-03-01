"""Panneau de contrôle latéral avec boutons et informations."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from pathlib import Path

from voronoi.core.geometry import Point


class ControlPanel(tk.Frame):
    """Panneau latéral avec les contrôles de l'application."""

    PANEL_WIDTH: int = 280
    BG_COLOR: str = "#ECEFF1"
    ACCENT_COLOR: str = "#2C3E50"
    BTN_COLOR: str = "#3498DB"
    BTN_HOVER: str = "#2980B9"
    DANGER_COLOR: str = "#E74C3C"

    def __init__(
        self,
        parent: tk.Widget,
        on_load: Callable[[Path], None],
        on_export: Callable[[str, Path], None],
        on_clear: Callable[[], None],
        on_remove_point: Callable[[int], None],
    ) -> None:
        super().__init__(parent, bg=self.BG_COLOR, width=self.PANEL_WIDTH)
        self.pack_propagate(False)

        self._on_load = on_load
        self._on_export = on_export
        self._on_clear = on_clear
        self._on_remove_point = on_remove_point

        self._format_var = tk.StringVar(value="PNG")
        self._point_count_var = tk.StringVar(value="Points : 0")
        self._compute_time_var = tk.StringVar(value="Calcul : -- ms")
        self._file_label_var = tk.StringVar(value="Aucun fichier chargé")

        self._points_listbox: Optional[tk.Listbox] = None
        self._points: list[Point] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crée tous les widgets du panneau."""
        title = tk.Label(
            self,
            text="Contrôles",
            font=("Helvetica", 16, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
        )
        title.pack(pady=(15, 10))

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=15, pady=5)

        self._create_file_section()
        self._create_format_section()
        self._create_export_section()
        self._create_info_section()
        self._create_point_list()
        self._create_clear_section()

    def _create_file_section(self) -> None:
        """Section de chargement de fichier."""
        frame = tk.LabelFrame(
            self,
            text="Charger Points",
            font=("Helvetica", 11, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", padx=15, pady=(10, 5))

        btn = tk.Button(
            frame,
            text="Charger fichier .txt",
            command=self._on_load_click,
            bg=self.BTN_COLOR,
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        btn.pack(fill="x")

        file_label = tk.Label(
            frame,
            textvariable=self._file_label_var,
            font=("Helvetica", 9),
            bg=self.BG_COLOR,
            fg="#7F8C8D",
            wraplength=230,
        )
        file_label.pack(pady=(5, 0))

    def _create_format_section(self) -> None:
        """Section de sélection du format d'export."""
        frame = tk.LabelFrame(
            self,
            text="Format Export",
            font=("Helvetica", 11, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", padx=15, pady=5)

        for fmt in ("PNG", "SVG"):
            rb = tk.Radiobutton(
                frame,
                text=fmt,
                variable=self._format_var,
                value=fmt,
                font=("Helvetica", 10),
                bg=self.BG_COLOR,
                activebackground=self.BG_COLOR,
                selectcolor=self.BG_COLOR,
            )
            rb.pack(anchor="w")

    def _create_export_section(self) -> None:
        """Bouton d'export."""
        btn = tk.Button(
            self,
            text="Exporter Diagramme",
            command=self._on_export_click,
            bg="#27AE60",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
        )
        btn.pack(fill="x", padx=15, pady=5)

    def _create_info_section(self) -> None:
        """Section d'informations (nombre de points, temps de calcul)."""
        frame = tk.LabelFrame(
            self,
            text="Informations",
            font=("Helvetica", 11, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", padx=15, pady=5)

        tk.Label(
            frame,
            textvariable=self._point_count_var,
            font=("Helvetica", 10),
            bg=self.BG_COLOR,
            fg="#2C3E50",
        ).pack(anchor="w")

        tk.Label(
            frame,
            textvariable=self._compute_time_var,
            font=("Helvetica", 10),
            bg=self.BG_COLOR,
            fg="#2C3E50",
        ).pack(anchor="w")

    def _create_point_list(self) -> None:
        """Liste scrollable des points avec possibilité de suppression."""
        frame = tk.LabelFrame(
            self,
            text="Liste Points",
            font=("Helvetica", 11, "bold"),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        list_frame = tk.Frame(frame, bg=self.BG_COLOR)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self._points_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            selectmode="single",
            bg="white",
            fg="#2C3E50",
            selectbackground=self.BTN_COLOR,
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#BDC3C7",
        )
        self._points_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self._points_listbox.yview)

        del_btn = tk.Button(
            frame,
            text="Supprimer sélectionné",
            command=self._on_delete_selected,
            bg=self.DANGER_COLOR,
            fg="white",
            font=("Helvetica", 9),
            relief="flat",
            padx=5,
            pady=3,
            cursor="hand2",
        )
        del_btn.pack(fill="x", pady=(5, 0))

    def _create_clear_section(self) -> None:
        """Bouton pour tout effacer."""
        btn = tk.Button(
            self,
            text="Tout Effacer",
            command=self._on_clear,
            bg=self.DANGER_COLOR,
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        btn.pack(fill="x", padx=15, pady=(5, 15))

    def _on_load_click(self) -> None:
        """Callback pour le bouton charger."""
        from voronoi.gui.dialogs import ask_open_file

        path = ask_open_file(self)
        if path:
            self._file_label_var.set(f"Fichier : {path.name}")
            self._on_load(path)

    def _on_export_click(self) -> None:
        """Callback pour le bouton exporter."""
        from voronoi.gui.dialogs import ask_save_file

        fmt = self._format_var.get()
        path = ask_save_file(self, fmt)
        if path:
            self._on_export(fmt, path)

    def _on_delete_selected(self) -> None:
        """Supprime le point sélectionné dans la listbox."""
        if not self._points_listbox:
            return
        sel = self._points_listbox.curselection()
        if sel:
            self._on_remove_point(sel[0])

    def update_point_count(self, count: int) -> None:
        """Met à jour l'affichage du nombre de points."""
        self._point_count_var.set(f"Points : {count}")

    def update_computation_time(self, ms: float) -> None:
        """Met à jour l'affichage du temps de calcul."""
        self._compute_time_var.set(f"Calcul : {ms:.1f} ms")

    def update_points_list(self, points: list[Point]) -> None:
        """Met à jour la listbox avec les points actuels."""
        self._points = list(points)
        if self._points_listbox:
            self._points_listbox.delete(0, tk.END)
            for p in points:
                self._points_listbox.insert(tk.END, f"({p.x:.0f}, {p.y:.0f})")
