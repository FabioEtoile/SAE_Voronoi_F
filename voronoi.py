from PIL import Image, ImageDraw

def lire_points(fichier):
    points = []
    f = open(fichier, 'r')
    for ligne in f:
        coordonnees = ligne.split(",")
        x = float(coordonnees[0])
        y = float(coordonnees[1])
        points.append((x,y))
    f.close()
    return points

points = lire_points("points.txt")

largeur = 50
hauteur = 50

# Source https://stackoverflow.com/questions/14831248/pil-selection-of-coordinates-to-make-an-image
img = Image.new("RGB", (largeur, hauteur), "white")
draw = ImageDraw.Draw(img)

rayon = 1

for (x,y) in points:
    # Source https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
    draw.circle((x,y), rayon,fill="black")

img.show()
img.save("points.png")