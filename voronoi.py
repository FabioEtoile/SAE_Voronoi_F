import drawsvg as dw

""" 
Lecture des points d'un fichier ligne par ligne 
Argument : Fichier.txt contenant les points
Retourne : Un tableau contenant les coordonnées x,y de chaque points
Exemple : [(2.0, 4.0), (5.3, 4.5), (18.0, 29.0), (12.5, 23.7)]
"""
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

mediatrice = []

# (x1+x2)/2 , (y1+y2/2) = Coordonnées du point entre les deux points
for i in range(len(points)):
    for j in range(len(points)):
        point_actuel = points[i]
        point_suivant = points[j]
        # Ne pas compter quand ce sont les mêmes points
        if point_actuel != point_suivant:
            xm = (point_actuel[0] + point_suivant[0]) / 2 
            ym = (point_actuel[1] + point_suivant[1]) / 2 

            mediatrice.append((xm,ym))

print(mediatrice)

# Création du SVG avec les points

# Source https://cduck.github.io/drawsvg/
d = dw.Drawing(largeur, hauteur)
d.append(dw.Rectangle(0, 0, largeur, hauteur, fill="white"))
rayon = 1

for (x,y) in points:
     d.append(dw.Circle(x, y, rayon, fill="black"))
for (x,y) in mediatrice:
     d.append(dw.Circle(x, y, rayon, fill="red"))
d.save_svg("points.svg")

