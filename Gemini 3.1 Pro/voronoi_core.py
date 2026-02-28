import math
import random
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw

# Types personnalisés pour la clarté
Point = Tuple[float, float]
Polygon = List[Point]

class VoronoiEngine:
    """Moteur de calcul du diagramme de Voronoï via l'intersection de demi-plans."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Boîte englobante initiale (le canvas)
        self.bbox: Polygon = [(0, 0), (width, 0), (width, height), (0, height)]

    def _clip_polygon(self, poly: Polygon, p: Point, q: Point) -> Polygon:
        """
        Découpe un polygone par la médiatrice entre p et q (Algorithme de Sutherland-Hodgman).
        Conserve la partie du polygone du côté de p.
        """
        # M est le milieu de [pq]
        mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
        # N est le vecteur normal pointant de q vers p
        nx, ny = p[0] - q[0], p[1] - q[1]

        def is_inside(pt: Point) -> bool:
            # Produit scalaire pour savoir si on est du côté de p
            return (pt[0] - mx) * nx + (pt[1] - my) * ny >= -1e-9

        def intersect(a: Point, b: Point) -> Optional[Point]:
            dx, dy = b[0] - a[0], b[1] - a[1]
            num = (mx - a[0]) * nx + (my - a[1]) * ny
            den = dx * nx + dy * ny
            if abs(den) < 1e-9:
                return None
            t = num / den
            return (a[0] + t * dx, a[1] + t * dy)

        new_poly = []
        n = len(poly)
        if n == 0:
            return new_poly

        for i in range(n):
            a = poly[i]
            b = poly[(i + 1) % n]

            if is_inside(a):
                new_poly.append(a)
                if not is_inside(b):
                    pt = intersect(a, b)
                    if pt: new_poly.append(pt)
            else:
                if is_inside(b):
                    pt = intersect(a, b)
                    if pt: new_poly.append(pt)

        return new_poly

    def compute_cells(self, points: List[Point]) -> List[Tuple[Point, Polygon]]:
        """Calcule les cellules de Voronoï pour une liste de points."""
        cells = []
        # Retirer les doublons tout en gardant l'ordre
        unique_points = list(dict.fromkeys(points))
        
        for p in unique_points:
            poly = self.bbox.copy()
            for q in unique_points:
                if p == q:
                    continue
                poly = self._clip_polygon(poly, p, q)
                if not poly: # Si le polygone disparaît, on arrête (optimisation)
                    break
            cells.append((p, poly))
        return cells

def get_color_for_point(point: Point) -> str:
    """Génère une couleur hexadécimale pastel déterministe basée sur les coordonnées."""
    random.seed(hash(point))
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def export_to_svg(cells: List[Tuple[Point, Polygon]], width: int, height: int, filepath: str):
    """Exporte les cellules au format SVG vectoriel."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
        for point, poly in cells:
            if not poly: continue
            points_str = " ".join([f"{x},{y}" for x, y in poly])
            color = get_color_for_point(point)
            f.write(f'  <polygon points="{points_str}" fill="{color}" stroke="black" stroke-width="1"/>\n')
            f.write(f'  <circle cx="{point[0]}" cy="{point[1]}" r="3" fill="black"/>\n')
        f.write('</svg>\n')

def export_to_png(cells: List[Tuple[Point, Polygon]], width: int, height: int, filepath: str):
    """Exporte les cellules au format image PNG."""
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    for point, poly in cells:
        if not poly: continue
        color = get_color_for_point(point)
        # Convertir les floats en tuples pour PIL
        poly_tuples = [(x, y) for x, y in poly]
        draw.polygon(poly_tuples, fill=color, outline="black")
        
        # Dessiner le point
        r = 3
        x, y = point
        draw.ellipse((x-r, y-r, x+r, y+r), fill="black")
        
    image.save(filepath, "PNG")