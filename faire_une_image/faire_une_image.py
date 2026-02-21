from PIL import Image
im = Image.new('RGB',(500,500))

# http://patrick.thevenon.free.fr/Docs/2019/2019_2SNT_Acti03_Image_python.pdf
# C'est pour créer une image 

for x in range(100):
    for y in range(500):
        im.putpixel((x,y),(0,255,0))
im.show()
im.save('vert_et_noir.png')