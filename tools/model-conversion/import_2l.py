"""Import the supplied MAX into a separate Blender process; keep an audit report."""
import bpy
import importlib.util
import json
from pathlib import Path
import time
import traceback
import sys
import faulthandler
import struct
import array
import hashlib
import argparse
from mathutils import Matrix, Vector

sys.stdout.reconfigure(line_buffering=True)
faulthandler.dump_traceback_later(60, repeat=True)

ROOT = Path(r'C:\projects\temir-gidro')
parser=argparse.ArgumentParser()
parser.add_argument('--assembly',default='2l2')
parser.add_argument('--slug',default='2l')
parser.add_argument('--index-only',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT = ROOT / 'output/models' / args.slug
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('max_importer', ROOT / 'output/model-conversion/io_scene_max/source/import_max.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# Keep container slices as views into the source, rather than retaining copies
# of every ancestor of a large mesh. Leaves keep the importer's original types.
parse_count = 0
parse_time = time.monotonic()
def next_chunk(self, superid, data, offset, level, number, conReader, primReader):
    global parse_count, parse_time
    header = 6
    typ, siz = struct.unpack_from('<Hi', data, offset)
    chunksize = siz & module.UNKNOWN_SIZE
    if siz == 0:
        siz = struct.unpack_from('<q', data, offset + 6)[0]
        header = 14
        chunksize = siz & module.MAXFILE_SIZE
    if chunksize < header or offset + chunksize > len(data):
        raise ValueError(f'Invalid chunk {typ:x} at {offset}, size {chunksize}, remaining {len(data)-offset}')
    payload = memoryview(data)[offset+header:offset+chunksize]
    if siz < 0:
        chunk = conReader(superid, typ, level, number, chunksize, None, primReader)
        chunk.set_data(payload)
    else:
        chunk = primReader(superid, typ, level, number, chunksize, None)
        chunk.set_data(bytes(payload))
    parse_count += 1
    if time.monotonic()-parse_time > 10:
        print('PARSE', parse_count, 'level',level,'offset',offset,'chunk',hex(typ),'size',chunksize, flush=True)
        parse_time = time.monotonic()
    return offset+chunksize, chunk
module.ChunkReader.get_next_chunk = next_chunk
def lazy_container(self, data):
    self._payload = data
    self._children = None
def lazy_children(self):
    if self._children is None:
        reader = module.ChunkReader()
        container_type = module.SceneChunk if isinstance(self, module.SceneChunk) else module.ContainerChunk
        self._children = reader.get_chunks(self.superid, self._payload, 1, container_type, self.primReader)
    return self._children
module.ContainerChunk.set_data = lazy_container
module.SceneChunk.set_data = lazy_container
module.ContainerChunk.children = property(lazy_children)
module.SceneChunk.children = property(lazy_children)
original_set = module.ByteArrayChunk.set_data
def compact_set(self, data):
    # Dense float coordinates have the same indexing/slicing behavior with
    # a typed array and avoid allocating one Python object per coordinate.
    if self.types in module.TYP_ARRAY and len(data) % 4 == 0:
        self.data = array.array('f', data)
    elif self.types in module.TYP_SHORT and len(data) % 2 == 0:
        self.data = array.array('H', data)
    else:
        original_set(self, data)
module.ByteArrayChunk.set_data = compact_set
if args.index_only:
    def index_scene(context, settings, mscale, transform, parent):
        records = []
        for i, chunk in enumerate(parent.children):
            name = module.get_node_name(chunk)
            guid = module.get_guid(chunk)
            info = dict(index=i, name=name, guid=hex(guid), cls=module.get_cls_name(chunk),
                size=len(getattr(chunk,'_payload',b'')))
            if module.get_node_parent(chunk) or guid == 1:
                prs, mesh, mat, lyr = module.get_matrix_mesh_material(chunk)
                info.update(mesh=module.get_cls_name(mesh) if mesh else None,
                    material=module.get_node_name(mat) if mat else None,
                    parent=module.get_node_name(module.get_node_parent(chunk)),
                    mesh_index=parent.children.index(mesh) if mesh else None,
                    mesh_size=len(getattr(mesh,'_payload',b'')) if mesh else None,
                    matrix=[list(v) for v in module.create_matrix(prs)])
                if name in ['2l2','ferma_1','ferma_2','Platforma','Group004'] or i==116940:
                    info['pivot']={hex(t):list(chunk.get_first(t).data) if chunk.get_first(t) else None for t in [0x96a,0x96b,0x96c]}
            records.append(info)
        (OUT/'max-index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        print('INDEX',len(records),flush=True)
    module.make_scene = index_scene
else:
    def selected_scene(context, settings, mscale, transform, parent):
        nodes=parent.children
        node_ids={id(n):i for i,n in enumerate(nodes)}
        roots=[i for i,n in enumerate(nodes) if module.get_node_name(n)==args.assembly]
        if len(roots)!=1:
            raise RuntimeError(f'Expected one {args.assembly} assembly, got {roots}')
        parents={i:node_ids.get(id(module.get_node_parent(n))) for i,n in enumerate(nodes)}
        chosen=set(roots)
        while True:
            added={i for i,p in parents.items() if p in chosen}
            if added <= chosen: break
            chosen |= added
        world_cache={}
        def world(i):
            if i not in world_cache:
                prs=module.get_matrix_mesh_material(nodes[i])[0]
                local=module.create_matrix(prs)
                p=parents.get(i)
                world_cache[i]=(world(p)@local) if p is not None else local
            return world_cache[i]
        cache={}
        errors=[]
        cache_hits=0
        print('ASSEMBLY',len(chosen),'nodes',flush=True)
        for count,i in enumerate(sorted(chosen)):
            node=nodes[i]
            name=module.get_node_name(node)
            prs,msh,mat,lyr=module.get_matrix_mesh_material(node)
            if not msh or module.get_guid(msh)==module.DUMMY:
                continue
            digest=hashlib.sha256()
            digest.update(getattr(msh,'_payload',b''))
            digest.update(getattr(mat,'_payload',b''))
            for typ in (0x96A,0x96B,0x96C):
                c=node.get_first(typ)
                digest.update(bytes(c.data) if c and not isinstance(c.data,tuple) else repr(c.data if c else None).encode())
            key=digest.digest()
            try:
                if key in cache:
                    created=[]
                    for data in cache[key]:
                        o=bpy.data.objects.new(name,data)
                        context.collection.objects.link(o)
                        created.append(o)
                    cache_hits+=1
                else:
                    _,created=module.create_object(context,settings,node,True)
                    cache[key]=[o.data for o in created]
                for o in created:
                    o.name=f'{name[:50]}_{i}'
                    o['max_node_index']=i
                    o['source_name']=name
                    o.matrix_world=world(i)
            except Exception as exc:
                errors.append(dict(index=i,name=name,error=str(exc)))
            if count%250==0:
                print('OBJECTS',count,'/',len(chosen),'unique geometry',len(cache),'cache hits',cache_hits,'errors',len(errors),flush=True)
        (OUT/'geometry-report.json').write_text(json.dumps(dict(selected=len(chosen),unique=len(cache),cache_hits=cache_hits,errors=errors),ensure_ascii=False,indent=2),encoding='utf-8')
        print('ASSEMBLY_DONE',len(bpy.data.objects),'unique',len(cache),'errors',len(errors),flush=True)
    module.make_scene=selected_scene
for stage in ('read_class_data', 'read_config', 'read_directory', 'read_class_directory', 'read_video_postqueue', 'read_scene'):
    original = getattr(module, stage)
    def traced(*args, _original=original, _stage=stage, **kwargs):
        print('STAGE', _stage, 'START', flush=True)
        value = _original(*args, **kwargs)
        print('STAGE', _stage, 'DONE', flush=True)
        return value
    setattr(module, stage, traced)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
started = time.time()
print('IMPORT_START', flush=True)
error = None
try:
    module.load(None, bpy.context, filepath=r'C:\Users\user\Desktop\Подьемники\2l2.max', use_image_search=True, use_collection=True)
except Exception:
    error = traceback.format_exc()
    print(error, flush=True)

bpy.context.view_layer.update()
objects = []
for o in bpy.data.objects:
    points = [o.matrix_world @ __import__('mathutils').Vector(v) for v in o.bound_box] if o.type == 'MESH' else []
    objects.append(dict(name=o.name, type=o.type, location=list(o.location), dimensions=list(o.dimensions),
        min=[min(p[i] for p in points) for i in range(3)] if points else None,
        max=[max(p[i] for p in points) for i in range(3)] if points else None,
        vertices=len(o.data.vertices) if o.type == 'MESH' else 0,
        polygons=len(o.data.polygons) if o.type == 'MESH' else 0,
        materials=[s.material.name if s.material else None for s in o.material_slots],
        parent=o.parent.name if o.parent else None))
report = dict(seconds=time.time()-started, error=error, objects=objects,
    materials=[dict(name=m.name, color=list(m.diffuse_color), nodes=[n.type for n in m.node_tree.nodes] if m.node_tree else []) for m in bpy.data.materials],
    images=[dict(name=i.name, path=i.filepath, size=list(i.size)) for i in bpy.data.images])
(OUT/'import-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('IMPORT_SUMMARY', len(objects), len(bpy.data.materials), time.time()-started, flush=True)
if objects:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{args.slug}-imported.blend'), compress=True)
print('IMPORT_DONE', flush=True)
