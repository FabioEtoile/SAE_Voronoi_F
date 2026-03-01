from PIL import Image
import math 
import random


""" 
Lecture des points d'un fichier ligne par ligne 
Argument : Fichier.txt contenant les points
Retourne : Un tableau contenant les coordonnées x,y de chaque points
Exemple : [2, 4, 5, 4, 18, 29, 12, 23]

"""

def lire_points(fichier):
    points = []
    f = open(fichier, 'r')
    for ligne in f:
        coordonnees = ligne.split(",")
        x = int(coordonnees[0])
        y = int(coordonnees[1])
        points.append(x)
        points.append(y)

    f.close()
    return points



def voronoi_test():
    image = Image.new('RGB',(500,500))
    imgx, imgy = image.size

    # http://patrick.thevenon.free.fr/Docs/2019/2019_2SNT_Acti03_Image_python.pdf
    # C'est pour créer une image 

    # The .putpixel() method in Pillow is used to insert pixels onto an image.
    # sur le site : https://www.codecademy.com/resources/docs/pillow/image/putpixel


    #Le carré de la distance entre un point de coordonnées (x,y) et un autre de coordonnées (a,b) est (x-a)^2 +(y-b)^2

    # En tant que tel, si vous connaissez les coordonnées de A et l'équation qui représente la ligne séparant la région contenant A
    # de la région contenant D, tout ce dont vous avez besoin est de trouver les paramètres constants de la fonction linéaire 
    # en fonction des coordonnées de D 
    # et de comparer avec la règle de la ligne donnée.
    #sur le site https://www.reddit.com/r/HomeworkHelp/comments/rbj4xr/math_voronoi_problems_unsure_of_how_to_find/?tl=fr


# Ce programme va donc consisté pour chaque point a calculer la distance avec les noyaux(points spéciaux) et lorsque le point le plus proche 
# d'un noyau il fait alors part de sa cellule 
    # tab_abscisse = [56, 56, 77, 43]
    # tab_ordonnee = [445, 23, 78, 22]
    # germes = len(tab_abscisse)
    
    
    points = lire_points("points.txt")
    
    germes = len(points)//2

    Red = []
    Green = []
    Blue = []

    # pour pouvoir colorier les zones déterminer dans la boucle : for i in range(germes):
    # on sélectionne le hasard pour etre sur d'obtenir des couleurs différentes 
    for i in range(germes):
            Red.append(random.randrange(256))
            Green.append(random.randrange(256))
            Blue.append(random.randrange(256))


    for y in range(500):
        for x in range(500):
            #la distance minimale d'un point est toujours la meme: {705.6925676241744}
            distance_minimale = math.hypot(imgx-1, imgy-1)
            j = -1
            #pour chaque germe on vérifie sa distance avec un point 
            for i in range(0, len(points), 2):
                
                distance_avec_germe = math.hypot(points[i]-x, points[i+1]-y)
                print (points[i], points[i+1])
                
            # Si la distance avec le germe est inférieur à la distance minimale alors la distance minimale 
            # du germe deviens la distance avec le germe   
            # En gros si ce cas arrive c'est que le point selectionné est un germe, lui meme  
                if  distance_avec_germe < distance_minimale:
                        distance_minimale = distance_avec_germe
                        j = i//2
            image.putpixel((x,y),(Red[j],Green[j],Blue[j]))
            
    image.save('placer_point.png')
    image.show()
  

voronoi_test()