"""Structural validation of separate Phase 2 glTF. No mechanical accuracy inference."""
import json,struct,sys,math
from pathlib import Path
path=Path(sys.argv[1]);raw=path.read_bytes()
magic,version,size=struct.unpack_from('<4sII',raw)
assert magic==b'glTF' and version==2 and size==len(raw)
length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4E4F534A
g=json.loads(raw[20:20+length]);nodes=g['nodes'];names={n['name']:n for n in nodes if 'name' in n}
expected=['Block','Head_LH','Head_RH','Cover_LH','Cover_RH','HeadGasket_LH','HeadGasket_RH','Intake_NA','Cooler_Valley','Cooler_Gasket','Exhaust_LH','Exhaust_RH','Shield_LH','Shield_RH','RearFace','RearSealCarrier','Bellhousing_Envelope','Sump_L320','FrontCover']
for name in expected:
 assert name in names,name
 assert names[name]['extras']['assembly_key']
 assert names[name]['extras']['geometry_status'] in ['APPROXIMATE','UNVERIFIED_ENVELOPE']
assert {names[name]['extras']['assembly_key'] for name in expected}=={'Block','Cylinder heads','Valve covers','Intake manifold','Oil cooler','Exhaust & shields','Rear face','Bellhousing','Oil pan'}
assert not any(n.get('name','').startswith('REVIEW_STUDIO') for n in nodes)
anchors=[n for n in nodes if n.get('name','').startswith('anchor__')]
assert len(anchors)==12
for n in anchors:assert n['extras']['physical_feature'] is False and 'mesh' not in n
for ident in ['gallery','head-plugs','vacuum','cam']:
 assert names['anchor__'+ident]['extras']['evidence_status']=='UNVERIFIED_REGION'
parents={child:i for i,n in enumerate(nodes) for child in n.get('children',[])}
for n in anchors:
 parent=nodes[parents[nodes.index(n)]]
 assert parent['name'] in expected
assert nodes[parents[nodes.index(names['anchor__cooler'])]]['name']=='Cooler_Valley'
assert nodes[parents[nodes.index(names['anchor__pcv'])]]['name']=='Cover_RH'
mesh_nodes=[n for n in nodes if 'mesh' in n]
assert not any('plug' in n.get('name','').lower() or 'gallery' in n.get('name','').lower() for n in mesh_nodes)
triangles=0;draws=0
for m in g['meshes']:
 for p in m['primitives']:
  assert p.get('mode',4)==4
  triangles+=g['accessors'][p['indices']]['count']//3;draws+=1
  for a in p['attributes'].values():
   accessor=g['accessors'][a]
   for k in ['min','max']:
    for v in accessor.get(k,[]):assert math.isfinite(v)
assert triangles<180000 and draws<=60 and len(raw)<8*1024**2
assert not g.get('animations') and not g.get('cameras') and not g.get('images')
report={'file':path.name,'glb_bytes':len(raw),'triangles':triangles,'mesh_nodes':len(mesh_nodes),'draw_call_primitives':draws,'assembly_groups':len(expected),'diagnostic_anchors':len(anchors),'embedded_textures':len(g.get('images',[])),'checks':'PASS','limitations':'Structural checks only; no dimensional, fitment, fluid-function or service-access validation.'}
print(json.dumps(report,indent=2));path.with_name('validation.json').write_text(json.dumps(report,indent=2))
