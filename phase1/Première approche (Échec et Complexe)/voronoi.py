import drawsvg as dw
import math

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

def calculer_intersection(xm1, ym1, vx1, vy1, xm2, ym2, vx2, vy2):
    """
    Calcule l'intersection de deux droites
    Retourne (x, y)
    """

    # Source : https://openclassrooms.com/forum/sujet/calcul-du-point-d-intersection-de-deux-segments-21661
    # Source : https://fr.khanacademy.org/math/fr-v2-seconde-s/x16338c0e47eff42b:geometrie-droites-dans-le-plan-repere/x16338c0e47eff42b:equation-cartesienne-d-une-droite/v/standard-form-for-linear-equations#:~:text=L'%C3%A9quation%20cart%C3%A9sienne%20d'une,la%20droite%20avec%20les%20axes.

    A1 = -vy1
    B1 = vx1
    
    # Ax + By = C
    C1 = A1 * xm1 + B1 * ym1

    A2 = -vy2
    B2 = vx2
    C2 = A2 * xm2 + B2 * ym2

    determinant = A1 * B2 - A2 * B1

    # "On peut trouver une intersection seulement si [...] != 0 (sinon les droites sont parallèles)"

    if determinant == 0:
        return None 

    # Cramer pour trouver X et Y
    x = (C1 * B2 - C2 * B1) / determinant
    y = (A1 * C2 - A2 * C1) / determinant

    return (x, y)

# Non fonctionnel et trop compliqué
# def filtrer_intersections(intersections, points):
#     vrais_intersections = []
# 
#     for ix,iy in intersections:
#         distances = []
#         for px, py in points:
#             # Source : https://www.alloprof.qc.ca/fr/eleves/bv/mathematiques/math-la-distance-entre-deux-points-m1311
#             # Distance entre deux points = sqrt(x2-x1)²+(y2-y1)²
#             distance = math.sqrt((px - ix)**2 + (py - iy)**2)
#             distances.append(distance)
# 
#         plus_petite_distance = distances[0]
#         for distance in distances:
#             if distance < plus_petite_distance:
#                 plus_petite_distance = distance
# 
#         compteur = 0
#         for distance in distances:
#             print(f"Distance : {distance}")
#             print(f"Petite distance : {plus_petite_distance}")
#             if distance == plus_petite_distance:
#                 compteur += 1 
#         
#         if compteur >= 3:
#             point = (ix, iy)
#             if point not in vrais_intersections:
#                 vrais_intersections.append(point)
#     return vrais_intersections

def preparer_donnees_voronoi(points):
    mediatrice = []
    donnees_droites = []

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

                mediatrice.append((xm,ym))
                donnees_droites.append((xm,ym,vx_perpendiculaire,vy_perpendiculaire))
    return mediatrice, donnees_droites

def tracer_diagramme_voronoi(points, mediatrice, donnees_droites):
    largeur = 500
    hauteur = 500

    # Source : https://cduck.github.io/drawsvg/
    d = dw.Drawing(largeur, hauteur)
    d.append(dw.Rectangle(0, 0, largeur, hauteur, fill="white"))

    # On affiche les lignes
    for xm, ym, vx_p, vy_p in donnees_droites:
        longueur = hauteur
        x_debut = xm + vx_p * longueur
        y_debut = ym + vy_p * longueur
        x_fin = xm - vx_p * longueur
        y_fin = ym - vy_p * longueur
        d.append(dw.Line(x_debut, y_debut, x_fin, y_fin, stroke='blue'))

    intersections = []
    
    # On compare chaque droite avec toutes les autres
    for i in range(len(donnees_droites)):
        for j in range(i + 1, len(donnees_droites)): 
            d1 = donnees_droites[i]
            d2 = donnees_droites[j]
            
            # d[0]=xm, d[1]=ym, d[2]=vx, d[3]=vy
            point = calculer_intersection(d1[0], d1[1], d1[2], d1[3], d2[0], d2[1], d2[2], d2[3])
            
            if point != None:
                intersections.append(point)

    # Non fonctionnel
    # vrais_intersections = filtrer_intersections(intersections,points)
    # print(f"Nombre intersections {len(vrais_intersections)}")

    # Création du SVG avec les points
    rayon = 1

    for (x,y) in points:
         d.append(dw.Circle(x, y, rayon, fill="black"))
    for (x,y) in mediatrice:
         d.append(dw.Circle(x, y, rayon, fill="red"))
         
    # Intersections en vert

    # for (x, y) in vrais_intersections:
    for (x, y) in intersections:
        if 0 <= x <= largeur and 0 <= y <= hauteur:
            d.append(dw.Circle(x, y, 2, fill="green"))
            
    d.save_svg("points.svg")

# Programme principal
points = lire_points("points.txt")
mediatrice, donnees_droites = preparer_donnees_voronoi(points)
tracer_diagramme_voronoi(points, mediatrice, donnees_droites)