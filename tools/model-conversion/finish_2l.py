"""Create the PBR review edition and self-contained web GLB for the supplied 2L."""
import bpy
import numpy as np
import math
import json
import sys
from pathlib import Path
from mathutils import Matrix, Vector

sys.stdout.reconfigure(line_buffering=True)
ROOT=Path(r'C:\projects\temir-gidro')
OUT=ROOT/'output/models/2l'
WEB=ROOT/'docs/models/2l'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'2l-working.blend'))
objects=[o for o in bpy.data.objects if o.type=='MESH']
def srgb(hexvalue):
    c=[int(hexvalue[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1,)
def material(name,color,metal,rough):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=srgb(color)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=rough
    m.diffuse_color=srgb(color)
    return m
red=material('2L | Красная порошковая окраска','b72027',.12,.29)
graphite=material('2L | Графитовая платформа','373a3c',.18,.38)
steel=material('2L | Оцинкованная сталь и цепи','bfc5ca',.82,.28)
chrome=material('2L | Полированные штоки','d5d9df',.95,.17)
rubber=material('2L | Резина и шланги','181b1e',.0,.6)
logo=material('2L | Графитовая панель с логотипом','373a3c',.18,.38)
img=bpy.data.images.load(str(OUT/'2l-panel-basecolor.png'),check_existing=True)
img.pack()
n=next(n for n in logo.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
texture=logo.node_tree.nodes.new('ShaderNodeTexImage')
texture.image=img
logo.node_tree.links.new(texture.outputs['Color'],n.inputs['Base Color'])
remap={'Material #794':red,'Material #795':graphite,'Material #796_2L2':logo,'Material #797':graphite,
       'Material #787':chrome,'Material #80':steel,'Material #82':rubber}
meshes=list({o.data.as_pointer():o.data for o in objects}.values())
for m in meshes:
    for i,old in enumerate(m.materials):
        if old and old.name in remap:m.materials[i]=remap[old.name]
platform=next(o for o in objects if o.name.startswith('Platforma'))
plate=material('2L | Рифлёный стальной настил','747b80',.65,.4)
normal_image=bpy.data.images.load(str(OUT/'2l-plate-normal.png'),check_existing=True)
normal_image.colorspace_settings.is_data=True
normal_image.pack()
tree=plate.node_tree
principled=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
uvnode=tree.nodes.new('ShaderNodeUVMap')
uvnode.uv_map='PlateUV'
normal_texture=tree.nodes.new('ShaderNodeTexImage')
normal_texture.image=normal_image
normal_node=tree.nodes.new('ShaderNodeNormalMap')
normal_node.uv_map='PlateUV'
normal_node.inputs['Strength'].default_value=.45
tree.links.new(uvnode.outputs['UV'],normal_texture.inputs['Vector'])
tree.links.new(normal_texture.outputs['Color'],normal_node.inputs['Color'])
tree.links.new(normal_node.outputs['Normal'],principled.inputs['Normal'])
platform.data.materials.append(plate)
plate_index=len(platform.data.materials)-1
plate_uv=platform.data.uv_layers.new(name='PlateUV')
for loop in platform.data.loops:
    co=platform.data.vertices[loop.vertex_index].co
    plate_uv.data[loop.index].uv=(co.x/1000,co.y/1000)
for face in platform.data.polygons:
    if face.normal.z>.9 and abs(face.center.z+275)<8:face.material_index=plate_index

brand=material('2L | Заводская табличка ТЕМИР ГИДРО','ffffff',.1,.4)
brand_image=bpy.data.images.load(str(OUT/'2l-brand.png'),check_existing=True)
brand_image.pack()
brand_texture=brand.node_tree.nodes.new('ShaderNodeTexImage')
brand_texture.image=brand_image
brand_shader=next(n for n in brand.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
brand.node_tree.links.new(brand_texture.outputs['Color'],brand_shader.inputs['Base Color'])
label_width=480
label_height=label_width*brand_image.size[1]/brand_image.size[0]
for side in (-1,1):
    data=bpy.data.meshes.new('2L factory plate')
    y=side*1191
    data.from_pydata([(-label_width/2,y,430),(label_width/2,y,430),(label_width/2,y,430+label_height),(-label_width/2,y,430+label_height)],[],[(0,1,2,3)])
    uv=data.uv_layers.new(name='UVMap')
    for loop,xy in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=xy
    data.materials.append(brand)
    label=bpy.data.objects.new('2L | Заводская табличка',data)
    bpy.context.collection.objects.link(label)
    label.matrix_world=platform.matrix_world.copy()
    objects.append(label)
print('MATERIALS_READY',len(meshes),flush=True)

by_mesh={}
for o in objects:by_mesh.setdefault(o.data.as_pointer(),[]).append(o)
decimate_id=next(x.identifier for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items if x.identifier.startswith('DECIM'))
before=sum(len(o.data.polygons) for o in objects)
for k,group in enumerate(by_mesh.values()):
    representative=group[0]
    original=representative.data
    polygons=len(original.polygons)
    # Preserve major surfaces; simplify the many repeated fasteners and links.
    size=max(representative.dimensions)
    target=polygons
    if size<.25:target=min(polygons,180 if size>.08 else 96)
    elif polygons>100000:target=100000
    elif polygons>8000:target=int(polygons*.65)
    if target<polygons:
        mod=representative.modifiers.new('Web geometry reduction',decimate_id)
        mod.ratio=max(.02,target/polygons)
        depsgraph=bpy.context.evaluated_depsgraph_get()
        reduced=bpy.data.meshes.new_from_object(representative.evaluated_get(depsgraph),preserve_all_data_layers=True,depsgraph=depsgraph)
        representative.modifiers.remove(mod)
        for o in group:o.data=reduced
    mesh=representative.data
    mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=np.bool_))
    if hasattr(mesh,'set_sharp_from_angle'):mesh.set_sharp_from_angle(angle=math.radians(38))
    if k%20==0:print('REDUCE',k,'/',len(by_mesh),flush=True)
after=sum(len(o.data.polygons) for o in objects)
print('POLYGONS',before,'->',after,flush=True)

# Align the mast pair horizontally for the browser's front view.
rotate=Matrix.Rotation(math.radians(225),4,'Z')
for o in objects:o.matrix_world=rotate@o.matrix_world
bpy.context.view_layer.update()
low=np.full(3,np.inf)
high=np.full(3,-np.inf)
coordinate_cache={}
for o in objects:
    key=o.data.as_pointer()
    if key not in coordinate_cache:
        a=np.empty(len(o.data.vertices)*3,dtype=np.float32)
        o.data.vertices.foreach_get('co',a)
        coordinate_cache[key]=a.reshape(-1,3)
    m=np.array(o.matrix_world)
    points=coordinate_cache[key]@m[:3,:3].T+m[:3,3]
    low=np.minimum(low,points.min(axis=0))
    high=np.maximum(high,points.max(axis=0))
shift=Matrix.Translation(Vector((-(low[0]+high[0])/2,-(low[1]+high[1])/2,-low[2])))
for o in objects:o.matrix_world=shift@o.matrix_world
dimensions=(high-low).tolist()
print('DIMENSIONS',dimensions,flush=True)

# Web export merges static pieces to avoid thousands of draw calls.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.join()
joined=bpy.context.view_layer.objects.active
joined.name='2L — подъёмник'
bpy.context.view_layer.update()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_location=Vector((0,0,dimensions[2]/2))
        area.spaces.active.region_3d.view_distance=dimensions[2]*1.15
        area.spaces.active.clip_end=1000
        area.spaces.active.shading.type=next(i.identifier for i in area.spaces.active.shading.bl_rna.properties['type'].enum_items if i.identifier.startswith('MATER'))
for image in bpy.data.images:
    if image.source=='FILE' and image.users:image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'2l.blend'),compress=True)
print('BLEND_SAVED',flush=True)
options=dict(filepath=str(WEB/'2l.glb'),use_selection=True,export_materials='EXPORT',export_cameras=False,export_lights=False,
             export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_apply=True)
# Enum identifiers come from the installed exporter (GLB is a dynamic enum).
format_property=bpy.ops.export_scene.gltf.get_rna_type().properties['export_format']
available=[i.identifier for i in format_property.enum_items]
if available:options['export_format']=next(i for i in available if 'GLB' in i)
else:
    # Dynamic exporter enum is unavailable through RNA; its default is binary GLB.
    pass
bpy.ops.export_scene.gltf(**options)
report=dict(source='2l2.max',dimensions_m=dimensions,source_objects=len(objects),source_polygons=before,web_polygons=after,
            web_objects=1,materials=[m.name if m else None for m in joined.data.materials],file_bytes=(WEB/'2l.glb').stat().st_size,
            note='Geometry converted from the original MAX; PBR materials reconstructed against catalog references.')
(OUT/'export-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('EXPORTED',json.dumps(report,ensure_ascii=True),flush=True)
