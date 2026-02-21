import drawsvg as dw
import os

""" 
Lecture des points d'un fichier ligne par ligne 
Argument : Fichier.txt contenant les points
Retourne : Un tableau contenant les coordonnées x,y de chaque points
Exemple : [(2.0, 4.0), (5.3, 4.5), (18.0, 29.0), (12.5, 23.7)]
"""
def lire_points(fichier):
    points = []
    #verifier que le fichier existe avant d essayer de l ouvrir
    if not os.path.exists(fichier):
        print("Le fichier n'existe pas")
        return points
    # ooverture et fermeture du fichier auto
    with open(fichier, 'r') as f:
        for ligne in f:
            # .strip() équivalent à \n (espaces et saut de ligne)
            ligne = ligne.strip()
            if ligne:
                try:
                    coordonnees = ligne.split(",")
                    x = float(coordonnees[0])
                    y = float(coordonnees[1])
                    points.append((x,y))
                except:
                    print("erreur de format sur une ligne")
    return points

points = lire_points("points.txt")

largeur = 500
hauteur = 500
# on définit une cellule de base avec les 4 coins dans l'ordre  
cellule_initiale = [(0,0), (largeur,0), (largeur,hauteur), (0,hauteur)]
points_du_polygone = []
# Source : https://cduck.github.io/drawsvg/
d = dw.Drawing(largeur, hauteur)
d.append(dw.Rectangle(0, 0, largeur, hauteur, fill="white"))


mediatrice = []


for p in cellule_initiale:
    points_du_polygone.append(p[0])
    points_du_polygone.append(p[1])

# dictionnaire, pour chaque point, on donne la cellure entiere au debut 
cellules = {}
for p in points:
    # on fait la copie pour chaque point
    cellules[p] = list(cellule_initiale)

for p in cellules:
    cellule_actuelle = cellules [p]
#list x1,x2 etc etc pour ce polygone 
    affichage_coords = []
    for coord in cellule_actuelle:
        affichage_coords.append(coord[0])
        affichage_coords.append(coord[1])
    d.append(dw.Lines(*affichage_coords, close=True, fill='none', stroke='black'))

# (x1+x2)/2 , (y1+y2/2) = Coordonnées du point entre les deux points
for i in range(len(points)):
    for j in range(len(points)):
        point_actuel = points[i]
        point_suivant = points[j]
        # Ne pas compter quand ce sont les mêmes points
        if point_actuel != point_suivant:
            xm = (point_actuel[0] + point_suivant[0]) / 2 
            ym = (point_actuel[1] + point_suivant[1]) / 2 

            # Vecteur entre les deux points (AB = (xb-xa, yb-ya))
            vx = point_suivant[0] - point_actuel[0]
            vy = point_suivant[1] - point_actuel[1]

            # Source :  https://www.reddit.com/r/learnmath/comments/1jjbe37/how_to_find_vectors_that_are_orthogonal_to_a/?tl=fr
            # "Inverse les coordonnées et change le signe de l'une d'elles. Par exemple, [2,5] et [5,-2]"

            vx_perpendiculaire = -vy
            vy_perpendiculaire = vx

            longueur = hauteur

            x_debut = xm + vx_perpendiculaire * longueur
            y_debut = ym + vy_perpendiculaire * longueur
            x_fin = xm - vx_perpendiculaire * longueur
            y_fin = ym - vy_perpendiculaire * longueur

            d.append(dw.Line(x_debut, y_debut, x_fin, y_fin, stroke='blue'))

            mediatrice.append((xm,ym))

print(mediatrice)

# Création du SVG avec les points
rayon = 1

for (x,y) in points:
     d.append(dw.Circle(x, y, rayon, fill="black"))
for (x,y) in mediatrice:
     d.append(dw.Circle(x, y, rayon, fill="red"))
d.save_svg("points.svg")

