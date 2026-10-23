"""Build the 4X PBR edition from the original 4X2L MAX assembly."""
import bpy
import numpy as np
import math
import json
import sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion

sys.stdout.reconfigure(line_buffering=True)
ROOT=Path(r'C:\projects\temir-gidro')
OUT=ROOT/'output/models/4x'
WEB=ROOT/'docs/models/4x'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'4x-imported.blend'))
objects=[o for o in bpy.data.objects if o.type=='MESH']
source_polygons=sum(len(o.data.polygons) for o in objects)
source_objects=len(objects)

def srgb(value):
    values=[int(value[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values)+(1,)
def material(name,color,metal,rough):
    m=bpy.data.materials.new('4X | '+name)
    m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=srgb(color)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=rough
    m.diffuse_color=srgb(color)
    return m
red=material('Красная порошковая окраска','b72027',.12,.29)
graphite=material('Графитовая рама и платформа','303436',.22,.34)
steel=material('Полированные штоки и крепёж','cbd1d7',.9,.22)
black=material('Корпуса гидроцилиндров','181b1f',.35,.28)
rubber=material('Резина и уплотнения','151719',0,.64)
plate=material('Рифлёный стальной настил','686f73',.65,.39)

# Apply the MAX hierarchy's transforms, then align the broad face of the lift.
transform=Matrix.Scale(.001,4)@Matrix.Rotation(math.radians(-45),4,'Z')
for o in objects:
    o.data.transform(transform@o.matrix_world)
    o.matrix_world=Matrix.Identity(4)
    o.data.update()
    if o.name.startswith(('ferma_','Object0021_','Object0031_','Object0041_')):mat=red
    elif o.name.startswith('chrome_'):mat=steel
    elif o.name.startswith(('black_','Object_')):mat=black
    elif o.name.startswith('rubber_'):mat=rubber
    else:mat=graphite
    o.data.materials.clear()
    o.data.materials.append(mat)
    o.data.polygons.foreach_set('material_index',np.zeros(len(o.data.polygons),dtype=np.int32))

points=[]
for o in objects:
    a=np.empty(len(o.data.vertices)*3,dtype=np.float32)
    o.data.vertices.foreach_get('co',a)
    points.append(a.reshape(-1,3))
low=np.minimum.reduce([a.min(axis=0) for a in points])
high=np.maximum.reduce([a.max(axis=0) for a in points])
offset=Vector((-(low[0]+high[0])/2,-(low[1]+high[1])/2,-low[2]))
for o in objects:
    o.data.transform(Matrix.Translation(offset))
    o.data.update()
dimensions=(high-low).tolist()
print('NORMALIZED',dimensions,flush=True)

normal_image=bpy.data.images.load(str(ROOT/'output/models/2l/2l-plate-normal.png'),check_existing=True)
normal_image.colorspace_settings.is_data=True
normal_image.pack()
tree=plate.node_tree
shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
uvnode=tree.nodes.new('ShaderNodeUVMap')
uvnode.uv_map='DeckUV'
texture=tree.nodes.new('ShaderNodeTexImage')
texture.image=normal_image
normal=tree.nodes.new('ShaderNodeNormalMap')
normal.uv_map='DeckUV'
normal.inputs['Strength'].default_value=.45
tree.links.new(uvnode.outputs['UV'],texture.inputs['Vector'])
tree.links.new(texture.outputs['Color'],normal.inputs['Color'])
tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
color_image=bpy.data.images.load(str(OUT/'4x-plate-basecolor.jpg'),check_existing=True)
color_image.pack()
color_texture=tree.nodes.new('ShaderNodeTexImage')
color_texture.image=color_image
tree.links.new(uvnode.outputs['UV'],color_texture.inputs['Vector'])
tree.links.new(color_texture.outputs['Color'],shader.inputs['Base Color'])
# Object0061 is the visible solid lid; the 91CEBCAA part is underneath it.
# Both use the same projected UVs, with the black sidewalls kept intact.
plate_faces=0
visible_deck_faces=0
for deck in [o for o in objects if o.name.startswith(('91CEBCAA','Object0061'))]:
    deck.data.materials.append(plate)
    plate_index=len(deck.data.materials)-1
    deck_uv=deck.data.uv_layers.new(name='DeckUV')
    for loop in deck.data.loops:
        co=deck.data.vertices[loop.vertex_index].co
        deck_uv.data[loop.index].uv=(co.x*3,co.y*3)
    deck_top=max(v.co.z for v in deck.data.vertices)
    for face in deck.data.polygons:
        if face.normal.z>.85 and face.center.z>deck_top-.02:
            face.material_index=plate_index
            plate_faces+=1
            if deck.name.startswith('Object0061'):visible_deck_faces+=1
print('DECK_FACES',plate_faces,flush=True)
print('VISIBLE_DECK_FACES',visible_deck_faces,flush=True)
if not visible_deck_faces:raise RuntimeError('Visible platform top has no tread material')

# Use the supplied 4X logo artwork for thin factory labels on both long sides.
brand=material('Заводской логотип ТЕМИР ГИДРО','ffffff',.05,.4)
brand_image=bpy.data.images.load(str(OUT/'4x-brand.png'),check_existing=True)
brand_image.pack()
brand_texture=brand.node_tree.nodes.new('ShaderNodeTexImage')
brand_texture.image=brand_image
brand_shader=next(n for n in brand.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
brand.node_tree.links.new(brand_texture.outputs['Color'],brand_shader.inputs['Base Color'])
frame=next(o for o in objects if o.name.startswith('Object0061'))
frame_low=Vector(tuple(min(v.co[i] for v in frame.data.vertices) for i in range(3)))
frame_high=Vector(tuple(max(v.co[i] for v in frame.data.vertices) for i in range(3)))
width=.62
height=width*brand_image.size[1]/brand_image.size[0]
center_z=(frame_low.z+frame_high.z)/2
for side in (-1,1):
    y=(frame_low.y-.0008) if side<0 else (frame_high.y+.0008)
    vertices=[(-width/2,y,center_z-height/2),(width/2,y,center_z-height/2),(width/2,y,center_z+height/2),(-width/2,y,center_z+height/2)]
    data=bpy.data.meshes.new('4X factory plate')
    data.from_pydata(vertices,[],[(0,1,2,3)])
    uv=data.uv_layers.new(name='UVMap')
    coords=[(0,0),(1,0),(1,1),(0,1)] if side<0 else [(1,0),(0,0),(0,1),(1,1)]
    for loop,xy in zip(uv.data,coords):loop.uv=xy
    data.materials.append(brand)
    o=bpy.data.objects.new('4X | Заводская табличка',data)
    bpy.context.collection.objects.link(o)
    objects.append(o)

decimate_id=next(i.identifier for i in bpy.types.Modifier.bl_rna.properties['type'].enum_items if i.identifier.startswith('DECIM'))
reductions=[]
for o in objects:
    count=len(o.data.polygons)
    if o.name.startswith('chrome_'):
        modifier=o.modifiers.new('Web reduction',decimate_id)
        modifier.ratio=.30
        graph=bpy.context.evaluated_depsgraph_get()
        reduced=bpy.data.meshes.new_from_object(o.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
        o.modifiers.remove(modifier)
        o.data=reduced
    o.data.polygons.foreach_set('use_smooth',np.ones(len(o.data.polygons),dtype=np.bool_))
    if hasattr(o.data,'set_sharp_from_angle'):o.data.set_sharp_from_angle(angle=math.radians(38))
    reductions.append(dict(name=o.name,before=count,after=len(o.data.polygons)))
print('GEOMETRY_READY',sum(len(o.data.polygons) for o in objects),flush=True)

scene=bpy.context.scene
scene.unit_settings.scale_length=1
if scene.world:
    scene.world.color=(.15,.15,.15)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active
        space.region_3d.view_location=Vector((0,0,dimensions[2]/2))
        space.region_3d.view_distance=dimensions[2]*1.3
        space.region_3d.view_rotation=Vector((1,-1,.3)).to_track_quat('Z','Y')
        space.clip_end=1000
        space.shading.type=next(i.identifier for i in space.shading.bl_rna.properties['type'].enum_items if i.identifier.startswith('MATER'))
# Keep an editable source with separate mechanisms, alongside the merged web file.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'4x-working.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=frame
bpy.ops.object.join()
joined=bpy.context.view_layer.objects.active
joined.name='4X — ножничный подъёмник'
joined.data.name='4X — геометрия для сайта'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'4x.blend'),compress=True)
properties=bpy.ops.export_scene.gltf.get_rna_type().properties
material_id=next(i.identifier for i in properties['export_materials'].enum_items if i.identifier=='EXPORT')
options=dict(filepath=str(WEB/'4x.glb'),use_selection=True,export_materials=material_id,export_cameras=False,export_lights=False,
             export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_apply=True)
formats=[i.identifier for i in properties['export_format'].enum_items]
if formats:options['export_format']=next(i for i in formats if 'GLB' in i)
bpy.ops.export_scene.gltf(**options)
report=dict(source='2l2.max',assembly='4X2L',dimensions_m=dimensions,source_objects=source_objects,source_polygons=source_polygons,
            web_objects=1,web_polygons=len(joined.data.polygons),file_bytes=(WEB/'4x.glb').stat().st_size,deck_faces=plate_faces,visible_deck_faces=visible_deck_faces,
            reductions=reductions,materials=[m.name for m in joined.data.materials])
(OUT/'export-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('EXPORTED',json.dumps(report,ensure_ascii=True),flush=True)
