from core.point import Point

def load_points_from_txt(filepath):
    points = []
    with open(filepath, "r") as f:
        for line in f:
            x, y = map(float, line.strip().split(","))
            points.append(Point(x, y))
    return points