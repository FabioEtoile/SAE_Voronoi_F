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

largeur = 1000
hauteur = 1000

# Source : https://cduck.github.io/drawsvg/
d = dw.Drawing(largeur, hauteur)
d.append(dw.Rectangle(0, 0, largeur, hauteur, fill="white"))


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


            '''
            Parcourt tous les autres points pour calculer le point milieu
            et le vecteur normal entre le point actuel et le point testé.
            Permet de déterminer la limite de la médiatrice.
            '''
            # Source : https://stackoverflow.com/questions/36063533/clipping-a-voronoi-diagram-python
            for k in range(len(points)):
                if k!= i and k!= j:
                    point_test = points[k]        
                    milieu_x = (point_actuel[0] + point_test[0]) / 2
                    milieu_y = (point_actuel[1] + point_test[1]) / 2
                    vecteur_normal_x = point_test[0] - point_actuel[0]
                    vecteur_normal_y = point_test[1] - point_actuel[1] 
                    # Source : https://github.com/mhdadk/sutherland-hodgman, 
                    # https://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping
                    # On calcule son vecteur par rapport au milieu puis par rapport à son produit scalaire.
                    delta_x_debut = x_debut - milieu_x
                    delta_y_debut = y_debut - milieu_y
                    produit_scalaire_debut = delta_x_debut * vecteur_normal_x + delta_y_debut * vecteur_normal_y

                    delta_x_fin = x_fin - milieu_x
                    delta_y_fin = y_fin - milieu_y
                    produit_scalaire_fin = delta_x_fin * vecteur_normal_x + delta_y_fin * vecteur_normal_y     

                    if produit_scalaire_debut > 0 and produit_scalaire_fin > 0:
                        break
                    elif produit_scalaire_debut > 0 or produit_scalaire_fin > 0:
                        # Source : https://github.com/scivision/lineclipping-python-fortran,
                        # https://gist.github.com/marmakoide/45d5389252683ae09c2df49d0548a627
                        t = produit_scalaire_debut / (produit_scalaire_debut - produit_scalaire_fin)
                        ix = x_debut + t * (x_fin - x_debut)
                        iy = y_debut + t * (y_fin - y_debut)
                        if produit_scalaire_debut > 0:
                            x_debut, y_debut = ix, iy
                        else:
                            x_fin, y_fin = ix, iy
            else:
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

