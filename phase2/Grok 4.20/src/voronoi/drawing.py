from typing import List, Tuple
from .core import Point, compute_voronoi_cells, get_bbox
import random

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import svgwrite
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False


def random_color() -> Tuple[int, int, int]:
    return (random.randint(30, 220), random.randint(30, 220), random.randint(30, 220))


def draw_voronoi_png(points: List[Point], width: int = 900, height: int = 700, filename: str = "voronoi.png"):
    if not PIL_AVAILABLE:
        raise ImportError("Pillow requis")
    bbox = get_bbox(points)
    cells = compute_voronoi_cells(points, bbox)

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    s = min(width / w, height / h) * 0.92
    ox = (width - s * w) / 2
    oy = (height - s * h) / 2

    def tf(p: Point):
        return ox + s * (p.x - xmin), oy + s * (p.y - ymin)

    colors = [random_color() for _ in points]

    for i, cell in enumerate(cells):
        if len(cell) < 3:
            continue
        pts = [tf(p) for p in cell]
        draw.polygon(pts, fill=colors[i], outline=(40,40,40), width=1)

    for p in points:
        x, y = tf(p)
        draw.ellipse((x-6, y-6, x+6, y+6), fill=(220,30,30))

    img.save(filename)


def draw_voronoi_svg(points: List[Point], width: int = 900, height: int = 700, filename: str = "voronoi.svg"):
    if not SVG_AVAILABLE:
        raise ImportError("svgwrite requis")
    bbox = get_bbox(points)
    cells = compute_voronoi_cells(points, bbox)

    dwg = svgwrite.Drawing(filename, size=(f"{width}px", f"{height}px"))

    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    s = min(width / w, height / h) * 0.92
    ox = (width - s * w) / 2
    oy = (height - s * h) / 2

    def tf(p: Point):
        return ox + s * (p.x - xmin), oy + s * (p.y - ymin)

    colors = [f"rgb{random_color()}" for _ in points]

    for i, cell in enumerate(cells):
        if len(cell) < 3:
            continue
        pts = [tf(p) for p in cell]
        dwg.add(dwg.polygon(points=pts, fill=colors[i], stroke="black", stroke_width=1))

    for p in points:
        x, y = tf(p)
        dwg.add(dwg.circle(center=(x, y), r=5, fill="red"))

    dwg.save()


def draw_voronoi_on_canvas(canvas, points: List[Point], width: int, height: int):
    bbox = get_bbox(points)
    cells = compute_voronoi_cells(points, bbox)

    xmin, ymin, xmax, ymax = bbox
    w = xmax - xmin
    h = ymax - ymin
    s = min(width / w, height / h) * 0.92
    ox = (width - s * w) / 2
    oy = (height - s * h) / 2

    def tf(p: Point):
        return ox + s * (p.x - xmin), oy + s * (p.y - ymin)

    colors = [f"#{random.randint(30,220):02x}{random.randint(30,220):02x}{random.randint(30,220):02x}" for _ in points]

    canvas.delete("all")

    for i, cell in enumerate(cells):
        if len(cell) < 3:
            continue
        pts = [tf(p) for p in cell]
        flat = [coord for pt in pts for coord in pt]
        canvas.create_polygon(flat, fill=colors[i], outline="black", width=1)

    for p in points:
        x, y = tf(p)
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="red")