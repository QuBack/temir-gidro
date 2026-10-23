from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math

source = Path('C:/Users/user/Desktop/Подьемники/maps')
output = Path('C:/projects/temir-gidro/output/models/2l')
names = ['2L2.tif', '2L2_logo_mask.tif', '2L2_logo_mask_gost.tif', '2x_git.jpg', '2k_texture_gost_.jpeg']
canvas = Image.new('RGB', (1000,350*len(names)), '#eceee9')
draw = ImageDraw.Draw(canvas)
for k, name in enumerate(names):
    image = Image.open(source/name)
    print(name, image.size, image.mode)
    image.thumbnail((960,300))
    canvas.paste(image.convert('RGB'), ((1000-image.width)//2, k*350+30))
    draw.text((15,k*350+8), name, fill='black')
canvas.save(output/'textures-contact.jpg')
base=Image.open(source/'2L2.tif').convert('RGB')
mask=Image.open(source/'2L2_logo_mask.tif').convert('L')
panel=Image.new('RGB',base.size,'#373a3c')
panel.paste(base,(0,0),mask)
panel=panel.resize((2048,2048),Image.Resampling.LANCZOS)
panel.save(output/'2l-panel-basecolor.png',optimize=True)
rows=[i for i,v in enumerate(mask.point(lambda p:255 if p>200 else 0).getprojection()[1]) if v]
bands=[]
for row in rows:
    if not bands or row>bands[-1][-1]+1:bands.append([])
    bands[-1].append(row)
band=max(bands,key=len)
region=mask.crop((0,int(band[0]),mask.width,int(band[-1]+1))).getbbox()
x0,_,x1,_=region
label=base.crop((max(0,x0-4),max(0,int(band[0])-4),min(base.width,x1+4),min(base.height,int(band[-1])+5)))
if label.height>label.width:label=label.transpose(Image.Transpose.ROTATE_90)
label.save(output/'2l-brand.png')
height=Image.open(source/'2k_texture_gost_bump.png').convert('L').resize((1024,1024),Image.Resampling.LANCZOS)
dx=height.filter(ImageFilter.Kernel((3,3),(-1,0,1,-2,0,2,-1,0,1),scale=2,offset=128))
dy=height.filter(ImageFilter.Kernel((3,3),(-1,-2,-1,0,0,0,1,2,1),scale=2,offset=128))
pixels=[]
for x,y in zip(dx.getdata(),dy.getdata()):
    nx,ny=(128-x)/90,(y-128)/90
    length=math.sqrt(nx*nx+ny*ny+1)
    pixels.append((round(127.5*(nx/length+1)),round(127.5*(ny/length+1)),round(127.5*(1/length+1))))
normal=Image.new('RGB',height.size)
normal.putdata(pixels)
normal.save(output/'2l-plate-normal.png',optimize=True)
