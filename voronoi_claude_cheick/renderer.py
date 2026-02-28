"""
Renderer module: export Voronoi diagrams to PNG and SVG.
Uses only Pillow (PNG) and standard library (SVG).
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Literal

from voronoi import VoronoiDiagram, Point, Edge


# ---------------------------------------------------------------------------
# Color palette helpers
# ---------------------------------------------------------------------------

_PALETTE = [
    (99, 179, 237),   # sky blue
    (154, 230, 180),  # mint
    (252, 211, 77),   # yellow
    (248, 113, 113),  # coral
    (167, 139, 250),  # lavender
    (251, 146, 60),   # orange
    (52, 211, 153),   # teal
    (236, 72, 153),   # pink
    (94, 234, 212),   # cyan
    (253, 186, 116),  # peach
]


def _site_color(index: int, alpha: int = 180) -> tuple[int, int, int, int]:
    r, g, b = _PALETTE[index % len(_PALETTE)]
    return r, g, b, alpha


def _darken(color: tuple[int, int, int], factor: float = 0.7) -> tuple[int, int, int]:
    return tuple(int(c * factor) for c in color)  # type: ignore


# ---------------------------------------------------------------------------
# Find nearest site for a pixel (used for cell coloring in PNG)
# ---------------------------------------------------------------------------

def _nearest_site_index(px: float, py: float, sites: list[Point]) -> int:
    best = 0
    best_dist = math.inf
    for i, s in enumerate(sites):
        d = (px - s.x) ** 2 + (py - s.y) ** 2
        if d < best_dist:
            best_dist = d
            best = i
    return best


# ---------------------------------------------------------------------------
# PNG export (Pillow)
# ---------------------------------------------------------------------------

def render_png(
    diagram: VoronoiDiagram,
    output_path: str,
    *,
    width: int = 800,
    height: int = 800,
    bg_color: tuple[int, int, int] = (15, 15, 25),
    edge_color: tuple[int, int, int, int] = (255, 255, 255, 220),
    site_radius: int = 5,
    fill_cells: bool = True,
    show_sites: bool = True,
) -> None:
    """Render diagram to a PNG file using Pillow."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise ImportError("Pillow is required for PNG export: pip install Pillow")

    x_min, y_min, x_max, y_max = diagram.bbox
    bw = x_max - x_min or 1
    bh = y_max - y_min or 1

    def to_px(p: Point) -> tuple[int, int]:
        px = int((p.x - x_min) / bw * width)
        py = int((p.y - y_min) / bh * height)
        return px, py

    img = Image.new("RGBA", (width, height), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Fill cells with soft colors
    if fill_cells and diagram.sites:
        sites = diagram.sites
        # Down-sampled fill (stride 2 for speed)
        stride = max(1, min(width, height) // 400)
        for py_img in range(0, height, stride):
            for px_img in range(0, width, stride):
                wx = px_img / width * bw + x_min
                wy = py_img / height * bh + y_min
                idx = _nearest_site_index(wx, wy, sites)
                r, g, b, _ = _site_color(idx, 100)
                for dy in range(stride):
                    for dx in range(stride):
                        if py_img + dy < height and px_img + dx < width:
                            img.putpixel((px_img + dx, py_img + dy), (r, g, b, 255))

    # Draw edges
    for edge in diagram.edges:
        if edge.is_complete():
            p1 = to_px(edge.start)
            p2 = to_px(edge.end)
            draw.line([p1, p2], fill=edge_color, width=2)

    # Draw sites
    if show_sites:
        for i, site in enumerate(diagram.sites):
            px, py = to_px(site)
            r, g, b, _ = _site_color(i)
            draw.ellipse(
                [(px - site_radius, py - site_radius), (px + site_radius, py + site_radius)],
                fill=(r, g, b, 255),
                outline=(255, 255, 255, 255),
                width=1,
            )

    # Save as RGB PNG
    img.convert("RGB").save(output_path, "PNG", optimize=True)


# ---------------------------------------------------------------------------
# SVG export (standard library only)
# ---------------------------------------------------------------------------

def render_svg(
    diagram: VoronoiDiagram,
    output_path: str,
    *,
    width: int = 800,
    height: int = 800,
    bg_color: str = "#0f0f19",
    edge_color: str = "rgba(255,255,255,0.85)",
    edge_width: float = 1.5,
    site_radius: float = 5.0,
    fill_cells: bool = True,
    show_sites: bool = True,
) -> None:
    """Render diagram to an SVG file using only standard library string building."""
    x_min, y_min, x_max, y_max = diagram.bbox
    bw = x_max - x_min or 1
    bh = y_max - y_min or 1

    def tx(x: float) -> float:
        return (x - x_min) / bw * width

    def ty(y: float) -> float:
        return (y - y_min) / bh * height

    lines: list[str] = []
    lines.append(f'<?xml version="1.0" encoding="utf-8"?>')
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    # Defs: clip path
    lines.append("  <defs>")
    lines.append(f'    <clipPath id="bbox">')
    lines.append(f'      <rect x="0" y="0" width="{width}" height="{height}"/>')
    lines.append(f'    </clipPath>')
    lines.append("  </defs>")

    # Background
    lines.append(f'  <rect width="{width}" height="{height}" fill="{bg_color}"/>')

    # Cell fill using Voronoi regions approximated via nearest-neighbour convex cells
    if fill_cells and diagram.sites:
        _svg_fill_cells(lines, diagram, tx, ty, width, height, x_min, y_min, bw, bh)

    # Edges group
    lines.append(f'  <g clip-path="url(#bbox)" stroke="{edge_color}" stroke-width="{edge_width}" stroke-linecap="round">')
    for edge in diagram.edges:
        if edge.is_complete():
            x1, y1 = tx(edge.start.x), ty(edge.start.y)
            x2, y2 = tx(edge.end.x), ty(edge.end.y)
            lines.append(f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    lines.append("  </g>")

    # Sites
    if show_sites:
        lines.append("  <g>")
        for i, site in enumerate(diagram.sites):
            r, g, b, _ = _site_color(i)
            cx, cy = tx(site.x), ty(site.y)
            lines.append(
                f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{site_radius}" '
                f'fill="rgb({r},{g},{b})" stroke="white" stroke-width="1.5"/>'
            )
        lines.append("  </g>")

    lines.append("</svg>")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def _svg_fill_cells(
    lines: list[str],
    diagram: VoronoiDiagram,
    tx, ty, width: int, height: int,
    x_min: float, y_min: float, bw: float, bh: float,
):
    """Approximate cell coloring in SVG using polygon paths built from edge vertices."""
    from collections import defaultdict

    sites = diagram.sites
    # Gather vertices per site pair using edges
    # Build cell polygons by collecting all vertices associated with each site
    site_vertices: dict[int, list[tuple[float, float]]] = defaultdict(list)

    for edge in diagram.edges:
        if not edge.is_complete():
            continue
        for site_ref, site_pt in [
            (edge.left_site, edge.left_site),
            (edge.right_site, edge.right_site),
        ]:
            if site_pt is None:
                continue
            # Find site index
            idx = next((i for i, s in enumerate(sites) if abs(s.x - site_pt.x) < 1e-6 and abs(s.y - site_pt.y) < 1e-6), None)
            if idx is None:
                continue
            site_vertices[idx].append((tx(edge.start.x), ty(edge.start.y)))
            site_vertices[idx].append((tx(edge.end.x), ty(edge.end.y)))

    # Add corners to each cell
    corners = [(0, 0), (width, 0), (width, height), (0, height)]

    lines.append('  <g clip-path="url(#bbox)" opacity="0.35">')
    for idx in range(len(sites)):
        r, g, b, _ = _site_color(idx)
        verts = site_vertices.get(idx, [])
        # Add corners that belong to this cell
        site_pt = sites[idx]
        for cx_px, cy_px in corners:
            wx = cx_px / width * bw + x_min
            wy = cy_px / height * bh + y_min
            nearest = _nearest_site_index(wx, wy, sites)
            if nearest == idx:
                verts.append((cx_px, cy_px))

        if len(verts) < 3:
            continue

        # Convex hull of vertices for the polygon
        hull = _convex_hull(verts)
        if len(hull) < 3:
            continue

        pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in hull)
        lines.append(f'    <polygon points="{pts_str}" fill="rgb({r},{g},{b})"/>')
    lines.append("  </g>")


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Graham scan convex hull."""
    pts = list(set(points))
    if len(pts) < 3:
        return pts
    pts.sort(key=lambda p: (p[1], p[0]))
    pivot = pts[0]

    def cross(O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    def angle_key(p):
        return math.atan2(p[1] - pivot[1], p[0] - pivot[0])

    pts = sorted(pts, key=angle_key)
    hull = []
    for p in pts:
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return hull
