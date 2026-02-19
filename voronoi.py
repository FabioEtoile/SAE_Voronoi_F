fichier = "points.txt"
points = []
f = open(fichier, 'r')

for ligne in f:
    coordonnees = ligne.split(",")
    x = float(coordonnees[0])
    y = float(coordonnees[1])
    points.append((x,y))

print(points)