import tkinter as tk
import voronoï_cheick
from PIL import Image, ImageTk #pour le format png 


#fentre tkinter 
root = tk.Tk()
root.title("Générateur Voronoï")
root.geometry("600x600")

label_image = tk.Label(root)
label_image.pack(pady=20)

# fonction déclanché lors du clic
def lancer_calcul():
    print("calcul en cours ...")
    voronoï_cheick.voronoi_test()
    print("calcul terminé")
    
    img = Image.open("placer_point.png")
    img_tk = ImageTk.PhotoImage(img)

    label_image.config(image=img_tk)
    label_image.image  = img_tk


# ajout du bouton
btn = tk.Button(root, text="Générer Voronoï", command=lancer_calcul)
btn.pack(pady=20) 

root.mainloop()