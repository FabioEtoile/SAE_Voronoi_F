import matplotlib.pyplot as plt
from core.point import Point

class Exporter:

    @staticmethod
    def export_png(cells, filename):
        fig, ax = plt.subplots()

        for site, polygon in cells.items():

            # 🔐 Protection contre polygone vide
            if not polygon:
                continue

            xs = [p.x for p in polygon] + [polygon[0].x]
            ys = [p.y for p in polygon] + [polygon[0].y]

            ax.plot(xs, ys)
            ax.plot(site.x, site.y, 'ro')

        ax.set_aspect('equal')
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def export_svg(cells, filename):
        fig, ax = plt.subplots()

        for site, polygon in cells.items():

            if not polygon:
                continue

            xs = [p.x for p in polygon] + [polygon[0].x]
            ys = [p.y for p in polygon] + [polygon[0].y]

            ax.plot(xs, ys)
            ax.plot(site.x, site.y, 'ro')

        ax.set_aspect('equal')
        plt.savefig(filename, format='svg')
        plt.close()