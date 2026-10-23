"""Normalize and inspect imported 2L without altering the source MAX."""
import bpy
import json
import hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
import sys

sys.stdout.reconfigure(line_buffering=True)
ROOT=Path(r'C:\projects\temir-gidro')
OUT=ROOT/'output/models/2l'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'2l-imported.blend'))
meshes=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)]
print('LOADED',len(meshes),flush=True)

cache={}
duplicates=0
signatures={}
for o in meshes:
    m=o.data
    h=hashlib.sha256()
    for collection,field,n,dtype in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.polygons,'loop_total',1,np.int32),(m.polygons,'material_index',1,np.int32)]:
        a=np.empty(len(collection)*n,dtype=dtype)
        collection.foreach_get(field,a)
        h.update(a.tobytes())
    for uv in m.uv_layers:
        a=np.empty(len(uv.data)*2,dtype=np.float32)
        uv.data.foreach_get('uv',a)
        h.update(a.tobytes())
    h.update('|'.join(mat.name if mat else '' for mat in m.materials).encode())
    key=h.hexdigest()
    signatures[o.name]=key
    if key in cache:
        o.data=cache[key]
        duplicates+=1
    else:cache[key]=m
print('GEOMETRY_UNIQUE',len(cache),'linked',duplicates,flush=True)

seen=set()
removed=0
for o in list(meshes):
    signature=(signatures[o.name],tuple(round(v,5) for row in o.matrix_world for v in row))
    if signature in seen:
        bpy.data.objects.remove(o,do_unlink=True)
        removed+=1
    else:seen.add(signature)
meshes=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)]
bpy.context.view_layer.update()
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
print('SOURCE_BOUNDS',list(lo),list(hi),'dimensions',list(hi-lo),flush=True)
# The CAD assembly is authored in millimetres. Keep real metres in glTF.
shift=Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))
normalize=Matrix.Scale(.001,4)@Matrix.Translation(shift)
for o in meshes:
    o.matrix_world=normalize@o.matrix_world
bpy.context.scene.unit_settings.scale_length=1
bpy.context.view_layer.update()

materials=[]
for m in bpy.data.materials:
    if not m.users:continue
    n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.node_tree else None
    materials.append(dict(name=m.name,users=m.users,color=list(m.diffuse_color),
        base=list(n.inputs['Base Color'].default_value) if n else None,
        metal=n.inputs['Metallic'].default_value if n else None,
        roughness=n.inputs['Roughness'].default_value if n else None,
        textures=[dict(name=n.image.name,path=n.image.filepath) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.node_tree else []))
report=dict(objects=len(meshes),unique_meshes=len({o.data.as_pointer() for o in meshes}),linked_duplicates=duplicates,overlapping_duplicates_removed=removed,
    source_min=list(lo),source_max=list(hi),dimensions_m=list((hi-lo)*.001),
    polygons=sum(len(o.data.polygons) for o in meshes),unique_polygons=sum(len(m.polygons) for m in cache.values()),materials=materials,
    largest=[dict(name=o.name,polygons=len(o.data.polygons),dimensions=list(o.dimensions),materials=[m.name if m else None for m in o.data.materials]) for o in sorted(meshes,key=lambda o:len(o.data.polygons),reverse=True)[:15]])
(OUT/'prepared-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('REPORT',json.dumps({k:v for k,v in report.items() if k not in ['materials','largest']}),flush=True)
for m in list(bpy.data.meshes):
    if not m.users:bpy.data.meshes.remove(m)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'2l-working.blend'),compress=True)
print('PREPARED',flush=True)
