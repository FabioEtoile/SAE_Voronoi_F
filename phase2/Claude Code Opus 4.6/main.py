"""Point d'entrée de l'application Voronoi Diagram Generator."""

from voronoi.gui.app import VoronoiApp


def main() -> None:
    app = VoronoiApp()
    app.run()


if __name__ == "__main__":
    main()
