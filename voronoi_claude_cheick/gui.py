"""
Voronoi GUI Application
A polished tkinter interface for computing and visualizing Voronoi diagrams.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import math
import os
from pathlib import Path
from typing import Optional

from voronoi import VoronoiDiagram, Point, parse_points_file
from renderer import render_png, render_svg


# ---------------------------------------------------------------------------
# Theme constants
# ---------------------------------------------------------------------------

class Theme:
    BG_DARK    = "#0d1117"
    BG_PANEL   = "#161b22"
    BG_INPUT   = "#1c2128"
    BG_HOVER   = "#21262d"
    ACCENT     = "#58a6ff"
    ACCENT_2   = "#3fb950"
    WARN       = "#f85149"
    TEXT_PRI   = "#e6edf3"
    TEXT_SEC   = "#8b949e"
    BORDER     = "#30363d"
    CANVAS_BG  = "#090c10"
    EDGE_CLR   = "#58a6ff"
    SITE_CLR   = "#f0883e"
    FONT_MONO  = ("Consolas", 10)
    FONT_BODY  = ("Segoe UI", 10)
    FONT_TITLE = ("Segoe UI Semibold", 11)
    FONT_H1    = ("Segoe UI Light", 18)

T = Theme  # alias


# ---------------------------------------------------------------------------
# Canvas Voronoi renderer (no image library needed for preview)
# ---------------------------------------------------------------------------

class CanvasRenderer:
    """Renders Voronoi diagram directly on a tkinter Canvas."""

    PALETTE = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
        "#f97316", "#06b6d4", "#ec4899", "#84cc16", "#6366f1",
    ]

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

    def render(self, diagram: VoronoiDiagram, fill_cells: bool = True, show_sites: bool = True):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 600

        x_min, y_min, x_max, y_max = diagram.bbox
        bw = x_max - x_min or 1
        bh = y_max - y_min or 1

        def tx(x): return (x - x_min) / bw * w
        def ty(y): return (y - y_min) / bh * h

        # Background
        self.canvas.create_rectangle(0, 0, w, h, fill=T.CANVAS_BG, outline="")

        if fill_cells and diagram.sites:
            self._draw_cells(diagram, tx, ty, w, h, x_min, y_min, bw, bh)

        # Draw edges
        for edge in diagram.edges:
            if edge.is_complete():
                self.canvas.create_line(
                    tx(edge.start.x), ty(edge.start.y),
                    tx(edge.end.x), ty(edge.end.y),
                    fill=T.EDGE_CLR, width=1.5, smooth=False,
                )

        # Draw sites
        if show_sites:
            for i, site in enumerate(diagram.sites):
                cx, cy = tx(site.x), ty(site.y)
                color = self.PALETTE[i % len(self.PALETTE)]
                r = 5
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                        fill=color, outline="white", width=1.5)
                self.canvas.create_text(cx + 8, cy - 8,
                                        text=f"({site.x:.0f},{site.y:.0f})",
                                        fill=T.TEXT_SEC, font=("Consolas", 8), anchor="w")

    def _draw_cells(self, diagram, tx, ty, w, h, x_min, y_min, bw, bh):
        """Draw Voronoi cells as colored polygons via a scanline nearest-site fill."""
        sites = diagram.sites
        if not sites:
            return
        # Rasterize cell boundaries with a low-res pass, then draw rectangles
        step = max(2, min(w, h) // 80)
        cell_rects: dict[int, list] = {i: [] for i in range(len(sites))}

        for py in range(0, int(h), step):
            for px in range(0, int(w), step):
                wx = px / w * bw + x_min
                wy = py / h * bh + y_min
                best, bd = 0, math.inf
                for i, s in enumerate(sites):
                    d = (wx - s.x) ** 2 + (wy - s.y) ** 2
                    if d < bd:
                        bd, best = d, i
                cell_rects[best].append((px, py, px + step, py + step))

        for i, rects in cell_rects.items():
            color = self.PALETTE[i % len(self.PALETTE)]
            # Convert hex to slightly transparent version via stipple isn't easy;
            # we draw with stipple pattern for translucency effect
            for x0, y0, x1, y1 in rects:
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=color, outline="", stipple="gray25",
                )


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

class VoronoiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voronoi Diagram Studio")
        self.geometry("1150x750")
        self.minsize(900, 600)
        self.configure(bg=T.BG_DARK)

        self._diagram: Optional[VoronoiDiagram] = None
        self._manual_points: list[Point] = []
        self._mode = tk.StringVar(value="file")  # "file" or "manual"
        self._fill_cells = tk.BooleanVar(value=True)
        self._show_sites = tk.BooleanVar(value=True)
        self._output_fmt = tk.StringVar(value="PNG")
        self._status = tk.StringVar(value="Ready.")
        self._file_path = tk.StringVar(value="")

        self._apply_ttk_styles()
        self._build_ui()

    # ------------------------------------------------------------------
    # TTK styles
    # ------------------------------------------------------------------

    def _apply_ttk_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=T.BG_DARK)
        style.configure("Panel.TFrame", background=T.BG_PANEL)
        style.configure("TLabel", background=T.BG_DARK, foreground=T.TEXT_PRI, font=T.FONT_BODY)
        style.configure("Sec.TLabel", background=T.BG_PANEL, foreground=T.TEXT_SEC, font=T.FONT_BODY)
        style.configure("Title.TLabel", background=T.BG_PANEL, foreground=T.TEXT_PRI, font=T.FONT_TITLE)
        style.configure("H1.TLabel", background=T.BG_DARK, foreground=T.ACCENT, font=T.FONT_H1)

        # Buttons
        style.configure("Accent.TButton",
                        background=T.ACCENT, foreground=T.BG_DARK,
                        font=("Segoe UI Semibold", 10), padding=(12, 6),
                        borderwidth=0, relief="flat")
        style.map("Accent.TButton",
                  background=[("active", "#79b8ff"), ("pressed", "#388bfd")])

        style.configure("Secondary.TButton",
                        background=T.BG_INPUT, foreground=T.TEXT_PRI,
                        font=T.FONT_BODY, padding=(10, 5),
                        borderwidth=1, relief="flat")
        style.map("Secondary.TButton",
                  background=[("active", T.BG_HOVER)])

        style.configure("Danger.TButton",
                        background="#6e2020", foreground=T.TEXT_PRI,
                        font=T.FONT_BODY, padding=(8, 4),
                        borderwidth=0)
        style.map("Danger.TButton",
                  background=[("active", T.WARN)])

        # Entry
        style.configure("TEntry",
                        fieldbackground=T.BG_INPUT, foreground=T.TEXT_PRI,
                        insertcolor=T.TEXT_PRI, borderwidth=1,
                        relief="flat")

        # Radiobutton
        style.configure("TRadiobutton",
                        background=T.BG_PANEL, foreground=T.TEXT_PRI,
                        font=T.FONT_BODY)
        style.map("TRadiobutton", background=[("active", T.BG_PANEL)])

        # Checkbutton
        style.configure("TCheckbutton",
                        background=T.BG_PANEL, foreground=T.TEXT_PRI,
                        font=T.FONT_BODY)
        style.map("TCheckbutton", background=[("active", T.BG_PANEL)])

        # Combobox
        style.configure("TCombobox",
                        fieldbackground=T.BG_INPUT, foreground=T.TEXT_PRI,
                        background=T.BG_INPUT, arrowcolor=T.TEXT_SEC,
                        selectbackground=T.ACCENT, selectforeground=T.BG_DARK)

        # Scrollbar
        style.configure("TScrollbar",
                        background=T.BG_PANEL, troughcolor=T.BG_DARK,
                        arrowcolor=T.TEXT_SEC, borderwidth=0)

        # Separator
        style.configure("TSeparator", background=T.BORDER)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ---- Header ----
        header = ttk.Frame(self, style="TFrame", padding=(20, 14, 20, 10))
        header.pack(fill="x", side="top")
        ttk.Label(header, text="Voronoi Diagram Studio", style="H1.TLabel").pack(side="left")
        ttk.Label(header, text="Fortune's Sweep Line Algorithm",
                  style="Sec.TLabel", background=T.BG_DARK).pack(side="left", padx=(16, 0), pady=(6, 0))

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x")

        # ---- Main layout ----
        main = ttk.Frame(self, style="TFrame")
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Left panel
        left = ttk.Frame(main, style="Panel.TFrame", padding=16, width=290)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)

        # Canvas area
        canvas_frame = ttk.Frame(main, style="TFrame")
        canvas_frame.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        self._build_left_panel(left)
        self._build_canvas(canvas_frame)

        # ---- Status bar ----
        status_bar = tk.Frame(self, bg=T.BG_PANEL, height=28)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self._status,
                 bg=T.BG_PANEL, fg=T.TEXT_SEC,
                 font=("Consolas", 9), anchor="w",
                 padx=14).pack(fill="x", pady=4)

    def _build_left_panel(self, parent):
        # Mode selection
        ttk.Label(parent, text="INPUT MODE", style="Title.TLabel",
                  background=T.BG_PANEL).pack(anchor="w", pady=(0, 8))

        modes_frame = ttk.Frame(parent, style="Panel.TFrame")
        modes_frame.pack(fill="x", pady=(0, 12))
        ttk.Radiobutton(modes_frame, text="From File (.txt)",
                        variable=self._mode, value="file",
                        command=self._on_mode_change,
                        style="TRadiobutton").pack(anchor="w")
        ttk.Radiobutton(modes_frame, text="Manual Entry",
                        variable=self._mode, value="manual",
                        command=self._on_mode_change,
                        style="TRadiobutton").pack(anchor="w", pady=(4, 0))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

        # File section
        self._file_frame = ttk.Frame(parent, style="Panel.TFrame")
        self._file_frame.pack(fill="x")
        ttk.Label(self._file_frame, text="FILE", style="Title.TLabel",
                  background=T.BG_PANEL).pack(anchor="w", pady=(0, 6))

        file_row = ttk.Frame(self._file_frame, style="Panel.TFrame")
        file_row.pack(fill="x")
        self._file_entry = ttk.Entry(file_row, textvariable=self._file_path,
                                     font=("Consolas", 9), width=18)
        self._file_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(file_row, text="Browse", style="Secondary.TButton",
                   command=self._browse_file).pack(side="left", padx=(4, 0))

        # Manual section
        self._manual_frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(self._manual_frame, text="MANUAL POINTS", style="Title.TLabel",
                  background=T.BG_PANEL).pack(anchor="w", pady=(0, 6))

        coord_row = ttk.Frame(self._manual_frame, style="Panel.TFrame")
        coord_row.pack(fill="x")

        ttk.Label(coord_row, text="x:", background=T.BG_PANEL,
                  foreground=T.TEXT_SEC, font=T.FONT_BODY).pack(side="left")
        self._mx = ttk.Entry(coord_row, width=6, font=T.FONT_MONO)
        self._mx.pack(side="left", padx=(2, 6))
        ttk.Label(coord_row, text="y:", background=T.BG_PANEL,
                  foreground=T.TEXT_SEC, font=T.FONT_BODY).pack(side="left")
        self._my = ttk.Entry(coord_row, width=6, font=T.FONT_MONO)
        self._my.pack(side="left", padx=(2, 0))

        btn_row = ttk.Frame(self._manual_frame, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_row, text="Add Point", style="Secondary.TButton",
                   command=self._add_manual_point).pack(side="left")
        ttk.Button(btn_row, text="Clear All", style="Danger.TButton",
                   command=self._clear_manual).pack(side="left", padx=(6, 0))

        # Points list
        list_frame = ttk.Frame(self._manual_frame, style="Panel.TFrame")
        list_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(list_frame, text="Points:", background=T.BG_PANEL,
                  foreground=T.TEXT_SEC, font=T.FONT_BODY).pack(anchor="w")
        self._pts_list = tk.Listbox(
            list_frame, bg=T.BG_INPUT, fg=T.TEXT_PRI,
            selectbackground=T.ACCENT, selectforeground=T.BG_DARK,
            font=T.FONT_MONO, height=7, bd=0, highlightthickness=0,
            relief="flat",
        )
        self._pts_list.pack(fill="x")
        ttk.Button(self._manual_frame, text="Remove Selected", style="Danger.TButton",
                   command=self._remove_selected_point).pack(anchor="w", pady=(4, 0))

        # Tip: click on canvas
        ttk.Label(self._manual_frame,
                  text="💡 Or click the canvas to add points",
                  background=T.BG_PANEL, foreground=T.ACCENT,
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 0))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

        # Render options
        ttk.Label(parent, text="RENDER OPTIONS", style="Title.TLabel",
                  background=T.BG_PANEL).pack(anchor="w", pady=(0, 8))

        opts = ttk.Frame(parent, style="Panel.TFrame")
        opts.pack(fill="x")
        ttk.Checkbutton(opts, text="Fill cells", variable=self._fill_cells,
                        style="TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(opts, text="Show sites", variable=self._show_sites,
                        style="TCheckbutton").pack(anchor="w", pady=(4, 0))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

        # Export
        ttk.Label(parent, text="EXPORT", style="Title.TLabel",
                  background=T.BG_PANEL).pack(anchor="w", pady=(0, 8))
        fmt_row = ttk.Frame(parent, style="Panel.TFrame")
        fmt_row.pack(fill="x", pady=(0, 6))
        ttk.Label(fmt_row, text="Format:", background=T.BG_PANEL,
                  foreground=T.TEXT_SEC, font=T.FONT_BODY).pack(side="left")
        fmt_cb = ttk.Combobox(fmt_row, textvariable=self._output_fmt,
                              values=["PNG", "SVG"], state="readonly", width=7)
        fmt_cb.pack(side="left", padx=(8, 0))

        ttk.Button(parent, text="Export File", style="Secondary.TButton",
                   command=self._export).pack(fill="x", pady=(0, 4))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

        # Compute button (primary CTA)
        ttk.Button(parent, text="▶  Compute Voronoi", style="Accent.TButton",
                   command=self._compute).pack(fill="x")

        self._on_mode_change()

    def _build_canvas(self, parent):
        ttk.Label(parent, text="DIAGRAM", style="Title.TLabel").pack(anchor="w", pady=(0, 4))

        canvas_border = tk.Frame(parent, bg=T.BORDER, bd=1)
        canvas_border.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_border, bg=T.CANVAS_BG,
            highlightthickness=0, cursor="crosshair",
        )
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._canvas_renderer = CanvasRenderer(self.canvas)
        self._draw_placeholder()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_mode_change(self):
        mode = self._mode.get()
        if mode == "file":
            self._manual_frame.pack_forget()
            self._file_frame.pack(fill="x")
        else:
            self._file_frame.pack_forget()
            self._manual_frame.pack(fill="x")

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select points file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self._file_path.set(path)

    def _add_manual_point(self):
        try:
            x = float(self._mx.get())
            y = float(self._my.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numeric x and y values.")
            return
        p = Point(x, y)
        self._manual_points.append(p)
        self._pts_list.insert("end", f"  ({x:.2f}, {y:.2f})")
        self._mx.delete(0, "end")
        self._my.delete(0, "end")
        self._set_status(f"{len(self._manual_points)} point(s) added.")

    def _remove_selected_point(self):
        sel = self._pts_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self._pts_list.delete(idx)
        self._manual_points.pop(idx)

    def _clear_manual(self):
        self._manual_points.clear()
        self._pts_list.delete(0, "end")
        self.canvas.delete("all")
        self._draw_placeholder()
        self._set_status("Cleared.")

    def _on_canvas_click(self, event):
        if self._mode.get() != "manual":
            return
        # Convert pixel to world coord (rough — no diagram yet)
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 600
        if self._diagram:
            x_min, y_min, x_max, y_max = self._diagram.bbox
            bw, bh = x_max - x_min, y_max - y_min
            wx = event.x / w * bw + x_min
            wy = event.y / h * bh + y_min
        else:
            wx = event.x / w * 600
            wy = event.y / h * 500
        p = Point(round(wx, 1), round(wy, 1))
        self._manual_points.append(p)
        self._pts_list.insert("end", f"  ({p.x:.1f}, {p.y:.1f})")
        # Draw a small dot
        r = 4
        self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r,
                                fill=T.SITE_CLR, outline="white", width=1)
        self._set_status(f"{len(self._manual_points)} point(s) — click Compute to generate.")

    def _on_canvas_resize(self, event):
        if self._diagram:
            self._redraw()

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    def _get_points(self) -> Optional[list[Point]]:
        if self._mode.get() == "file":
            path = self._file_path.get().strip()
            if not path:
                messagebox.showerror("No file", "Please select a .txt file.")
                return None
            try:
                return parse_points_file(path)
            except Exception as e:
                messagebox.showerror("Parse error", str(e))
                return None
        else:
            if len(self._manual_points) < 2:
                messagebox.showerror("Not enough points", "Add at least 2 points.")
                return None
            return list(self._manual_points)

    def _compute(self):
        points = self._get_points()
        if points is None:
            return
        self._set_status("Computing…")
        self.update_idletasks()

        def _work():
            try:
                diagram = VoronoiDiagram(points)
                diagram.compute(margin=60)
                self._diagram = diagram
                self.after(0, self._redraw)
                self.after(0, lambda: self._set_status(
                    f"Done. {len(diagram.sites)} sites, {len(diagram.edges)} edges."
                ))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.after(0, lambda: self._set_status("Error."))

        threading.Thread(target=_work, daemon=True).start()

    def _redraw(self):
        if self._diagram:
            self._canvas_renderer.render(
                self._diagram,
                fill_cells=self._fill_cells.get(),
                show_sites=self._show_sites.get(),
            )

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export(self):
        if self._diagram is None:
            messagebox.showwarning("Nothing to export", "Compute a diagram first.")
            return
        fmt = self._output_fmt.get().lower()
        path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(), f"*.{fmt}"), ("All files", "*.*")],
            title=f"Save as {fmt.upper()}",
        )
        if not path:
            return
        self._set_status("Exporting…")
        try:
            if fmt == "png":
                render_png(
                    self._diagram, path,
                    fill_cells=self._fill_cells.get(),
                    show_sites=self._show_sites.get(),
                )
            else:
                render_svg(
                    self._diagram, path,
                    fill_cells=self._fill_cells.get(),
                    show_sites=self._show_sites.get(),
                )
            self._set_status(f"Exported → {path}")
            messagebox.showinfo("Export successful", f"File saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))
            self._set_status("Export failed.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, msg: str):
        self._status.set(f"  {msg}")

    def _draw_placeholder(self):
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 600
        cx, cy = w // 2, h // 2
        self.canvas.create_text(
            cx, cy - 16,
            text="Add points or load a file,",
            fill=T.TEXT_SEC, font=("Segoe UI", 14),
        )
        self.canvas.create_text(
            cx, cy + 16,
            text="then click  ▶ Compute Voronoi",
            fill=T.ACCENT, font=("Segoe UI", 13),
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = VoronoiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
