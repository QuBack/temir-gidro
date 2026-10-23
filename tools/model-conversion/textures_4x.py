"""Extract the 4X factory label from its supplied texture atlas and mask."""
from PIL import Image, ImageEnhance
from pathlib import Path

ROOT=Path(r'C:\projects\temir-gidro')
SOURCE=Path('C:/Users/user/Desktop/Подьемники/maps')
OUT=ROOT/'output/models/4x'
base=Image.open(SOURCE/'4xl2_logo.tif').convert('RGB')
mask=Image.open(SOURCE/'4xl2_logo_mask.tif').convert('L').point(lambda p:255 if p>200 else 0)
rows=[i for i,v in enumerate(mask.getprojection()[1]) if v]
bands=[]
for row in rows:
    if not bands or row>bands[-1][-1]+1:bands.append([])
    bands[-1].append(row)
band=max(bands,key=len)
x0,_,x1,_=mask.crop((0,band[0],mask.width,band[-1]+1)).getbbox()
label=base.crop((max(0,x0-4),max(0,band[0]-4),min(base.width,x1+4),min(base.height,band[-1]+5)))
if label.height>label.width:label=label.transpose(Image.Transpose.ROTATE_90)
bright_rows=[i for i,v in enumerate(label.convert('L').point(lambda p:255 if p>220 else 0).getprojection()[1]) if v]
bright_bands=[]
for row in bright_rows:
    if not bright_bands or row>bright_bands[-1][-1]+1:bright_bands.append([])
    bright_bands[-1].append(row)
chosen=next(b for b in bright_bands if len(b)>20)
label=label.crop((0,max(0,chosen[0]-2),label.width,min(label.height,chosen[-1]+3)))
label.save(OUT/'4x-brand.png')
print('4X factory label',label.size)
plate_color=Image.open(SOURCE/'2k_texture_gost_.jpeg').convert('RGB')
plate_color=plate_color.resize((1024,1024),Image.Resampling.LANCZOS)
plate_color=ImageEnhance.Brightness(plate_color).enhance(.64)
plate_color.save(OUT/'4x-plate-basecolor.jpg',quality=90,optimize=True)
