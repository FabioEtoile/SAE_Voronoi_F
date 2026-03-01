import tkinter as tk
from tkinter import filedialog, messagebox
from core.voronoi import VoronoiDiagram
from core.exporter import Exporter
from utils.file_loader import load_points_from_txt
from core.point import Point

import os

class VoronoiGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Diagramme de Voronoï")
        self.points = []

        self.setup_ui()
        self.auto_load_default_file()

    def setup_ui(self):
        tk.Button(self.root, text="Charger fichier TXT", command=self.load_file).pack(pady=5)
        tk.Button(self.root, text="Ajouter point manuel", command=self.add_point).pack(pady=5)
        tk.Button(self.root, text="Générer PNG", command=self.generate_png).pack(pady=5)
        tk.Button(self.root, text="Générer SVG", command=self.generate_svg).pack(pady=5)

    def auto_load_default_file(self):
        default_path = os.path.join("data", "points.txt")
        if os.path.exists(default_path):
            try:
                self.points = load_points_from_txt(default_path)
                print(f"{len(self.points)} points chargés automatiquement.")
            except Exception as e:
                print(f"Erreur chargement automatique : {e}")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            self.points = load_points_from_txt(filepath)
            messagebox.showinfo("Succès", f"{len(self.points)} points chargés.")

    def add_point(self):
        win = tk.Toplevel(self.root)
        tk.Label(win, text="x:").pack()
        x_entry = tk.Entry(win)
        x_entry.pack()
        tk.Label(win, text="y:").pack()
        y_entry = tk.Entry(win)
        y_entry.pack()

        def save():
            x = float(x_entry.get())
            y = float(y_entry.get())
            self.points.append(Point(x, y))
            win.destroy()

        tk.Button(win, text="Ajouter", command=save).pack()

    def generate_png(self):
        if not self.points:
            messagebox.showerror("Erreur", "Aucun point.")
            return
        diagram = VoronoiDiagram(self.points)
        cells = diagram.compute()
        Exporter.export_png(cells, "result.png")
        messagebox.showinfo("Succès", "PNG généré.")

    def generate_svg(self):
        if not self.points:
            messagebox.showerror("Erreur", "Aucun point.")
            return
        diagram = VoronoiDiagram(self.points)
        cells = diagram.compute()
        Exporter.export_svg(cells, "result.svg")
        messagebox.showinfo("Succès", "SVG généré.")