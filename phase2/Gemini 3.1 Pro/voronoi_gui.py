import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from voronoi_core import VoronoiEngine, get_color_for_point, export_to_png, export_to_svg

class VoronoiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Diagramme de Voronoï")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        self.width = 800
        self.height = 600
        self.points = []
        self.engine = VoronoiEngine(self.width, self.height)

        self._build_gui()

    def _build_gui(self):
        # Panneau de contrôle (gauche)
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_frame, text="Contrôles", font=("Helvetica", 14, "bold")).pack(pady=(0, 20))

        ttk.Button(control_frame, text="Charger Fichier .txt", command=self.load_txt).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Effacer tout", command=self.clear_canvas).pack(fill=tk.X, pady=5)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Label(control_frame, text="Exportation").pack(pady=(0, 5))
        ttk.Button(control_frame, text="Exporter en PNG", command=lambda: self.export("png")).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Exporter en SVG", command=lambda: self.export("svg")).pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text="Note: Cliquez sur le\ncanevas pour ajouter\ndes points manuellement.", foreground="gray").pack(side=tk.BOTTOM, pady=20)

        # Canevas (droite)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(side=tk.RIGHT, padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def load_txt(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath: return
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    x, y = map(float, line.split(','))
                    self.points.append((x, y))
            self.draw()
        except Exception as e:
            messagebox.showerror("Erreur de lecture", f"Impossible de lire le fichier: {e}\nFormat attendu: x,y par ligne.")

    def on_canvas_click(self, event):
        self.points.append((float(event.x), float(event.y)))
        self.draw()

    def clear_canvas(self):
        self.points = []
        self.canvas.delete("all")

    def draw(self):
        self.canvas.delete("all")
        if not self.points: return

        cells = self.engine.compute_cells(self.points)
        for point, poly in cells:
            if not poly: continue
            color = get_color_for_point(point)
            
            # Formatage pour le canevas Tkinter
            flat_coords = [coord for p in poly for coord in p]
            if len(flat_coords) >= 6: # Un polygone valide a au moins 3 points
                self.canvas.create_polygon(flat_coords, fill=color, outline="black")
            
            # Dessiner le point
            r = 3
            x, y = point
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")

    def export(self, file_type):
        if not self.points:
            messagebox.showwarning("Vide", "Il n'y a aucun point à exporter.")
            return

        ext = f"*.{file_type}"
        filepath = filedialog.asksaveasfilename(defaultextension=f".{file_type}", filetypes=[(f"{file_type.upper()} files", ext)])
        if not filepath: return

        cells = self.engine.compute_cells(self.points)
        try:
            if file_type == "png":
                export_to_png(cells, self.width, self.height, filepath)
            elif file_type == "svg":
                export_to_svg(cells, self.width, self.height, filepath)
            messagebox.showinfo("Succès", f"Fichier {file_type.upper()} exporté avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'exportation: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()