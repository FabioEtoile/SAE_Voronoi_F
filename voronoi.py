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

print(points)