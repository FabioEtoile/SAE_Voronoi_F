# Anciennement app.py
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List

from src.voronoi.core import Point
from src.voronoi.drawing import draw_voronoi_png, draw_voronoi_svg, draw_voronoi_on_canvas


class VoronoiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diagramme de Voronoi – from scratch")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        self.points: List[Point] = []

        # ── Barre supérieure ───────────────────────────────────────────────
        top_frame = tk.Frame(root, padx=12, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Button(top_frame, text="Charger fichier .txt", command=self.load_file).pack(side=tk.LEFT, padx=6)

        tk.Label(top_frame, text="ou points manuels :").pack(side=tk.LEFT, padx=(20,6))

        self.points_entry = tk.Entry(top_frame, width=60)
        self.points_entry.pack(side=tk.LEFT, padx=6)
        self.points_entry.insert(0, "100,200 ; 300,450 ; 500,120 ; 250,600")

        tk.Button(top_frame, text="Charger ces points", command=self.load_manual).pack(side=tk.LEFT, padx=6)

        # ── Options sortie ─────────────────────────────────────────────────
        opt_frame = tk.Frame(root, padx=12, pady=8)
        opt_frame.pack(fill=tk.X)

        tk.Label(opt_frame, text="Format de sortie :").pack(side=tk.LEFT, padx=(0,12))

        self.output_type = tk.StringVar(value="PNG")
        tk.Radiobutton(opt_frame, text="PNG", variable=self.output_type, value="PNG").pack(side=tk.LEFT, padx=8)
        tk.Radiobutton(opt_frame, text="SVG", variable=self.output_type, value="SVG").pack(side=tk.LEFT, padx=8)

        tk.Button(opt_frame, text="Exporter image", command=self.export_image, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=10)

        # ── Zone de dessin ─────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, bg="#f8f9fa", highlightthickness=1, relief="ridge")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if self.points:
            self.display_voronoi()

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
            self.points = []
            for line in lines:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                x_str, y_str = line.split(',', 1)
                self.points.append(Point(float(x_str), float(y_str)))
            messagebox.showinfo("Chargement", f"{len(self.points)} points chargés.")
            self.display_voronoi()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def load_manual(self):
        text = self.points_entry.get().strip()
        if not text:
            return
        try:
            self.points = []
            for part in text.split(';'):
                part = part.strip()
                if not part:
                    continue
                x_str, y_str = part.split(',')
                self.points.append(Point(float(x_str.strip()), float(y_str.strip())))
            messagebox.showinfo("Chargement", f"{len(self.points)} points chargés.")
            self.display_voronoi()
        except Exception as e:
            messagebox.showerror("Erreur de format", str(e))

    def display_voronoi(self):
        if len(self.points) < 2:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width()//2,
                self.canvas.winfo_height()//2,
                text="Au moins 2 points requis",
                font=("Helvetica", 14), fill="gray"
            )
            return
        try:
            draw_voronoi_on_canvas(self.canvas, self.points,
                                 self.canvas.winfo_width(),
                                 self.canvas.winfo_height())
        except Exception as e:
            messagebox.showerror("Erreur de calcul", str(e))

    def export_image(self):
        if len(self.points) < 2:
            messagebox.showwarning("Action impossible", "Il faut au moins 2 points.")
            return

        ext = self.output_type.get().lower()
        path = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(f"Fichier {ext.upper()}", f"*.{ext}")]
        )
        if not path:
            return

        try:
            if ext == "png":
                draw_voronoi_png(self.points, filename=path)
            else:
                draw_voronoi_svg(self.points, filename=path)
            messagebox.showinfo("Succès", f"Fichier enregistré :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur d'export", str(e))


def main():
    root = tk.Tk()
    VoronoiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()