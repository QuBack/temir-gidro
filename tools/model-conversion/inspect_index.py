import json
import sys
from collections import Counter
from pathlib import Path
root=Path('C:/projects/temir-gidro/output/models/2l')
data=json.loads((root/'max-index.json').read_text(encoding='utf-8'))
objects=[x for x in data if 'mesh' in x]
print('OBJECTS',len(objects),'PARENTS',Counter(x.get('parent') for x in objects).most_common(18))
selected=[]
root_name=sys.argv[1] if len(sys.argv)>1 else '2l2'
names={root_name}
while True:
    new={x['name'] for x in objects if x.get('parent') in names}
    if new<=names:break
    names |= new
selected=[x for x in objects if x['name'] in names or x.get('parent') in names]
print('SELECTED',len(selected),'MESH_MB',sum(x.get('mesh_size') or 0 for x in selected)/1048576)
for x in selected[:30]:
    print(x['index'],x['name'][:85],x.get('parent'),x.get('mesh_index'),x.get('mesh_size'))
(root/f'{root_name}-selection-index.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
