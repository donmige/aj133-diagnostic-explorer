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
assert names['anchor__gallery']['extras']['evidence_status']=='DOCUMENTED_SOURCE_APPROXIMATE_REGION'
for ident in ['head-plugs','vacuum','cam']:
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
import hashlib
root=path.parent
diagnostic=json.loads((root/'diagnostic-data.json').read_text())
assert len(diagnostic['overlays'])==11 and len(diagnostic['camera_approaches'])==6
assert all('HYPOTHETICAL' in o['status'] for o in diagnostic['overlays'] if o['kind']=='hypothesis')
assert all(c['status']=='PROPOSED_CAMERA_APPROACH_NOT_VERIFIED_CLEARANCE' for c in diagnostic['camera_approaches'])
extra=(root/'aj133-phase2b-overlays.glb').read_bytes();length=struct.unpack_from('<I',extra,12)[0];extra_json=json.loads(extra[20:20+length])
assert len([n for n in extra_json['nodes'] if n.get('extras',{}).get('role')=='diagnostic_overlay' and 'mesh' not in n])==11
for n in extra_json['nodes']:
 if 'mesh' in n:assert n['extras']['physical_feature'] is False
fallback_hashes=json.loads((root/'fallback-sha256.json').read_text())
for name,expected_hash in fallback_hashes.items():assert hashlib.sha256((root/'fallback-phase2'/name).read_bytes()).hexdigest()==expected_hash
report.update({'diagnostic_overlay_groups':11,'camera_proposals':6,'physical_gallery_plugs_added':0,'fallback_hashes_preserved':True,'physical_asset_sha256':hashlib.sha256(raw).hexdigest(),'overlay_glb_bytes':len(extra)})
# Decode actual binary positions/indices, beyond accessor bounds checks.
bin_start=28+struct.unpack_from('<I',raw,12)[0]
degenerate_count=0;finite_vertex_count=0
for m in g['meshes']:
 for primitive in m['primitives']:
  pa=g['accessors'][primitive['attributes']['POSITION']];pv=g['bufferViews'][pa['bufferView']]
  start=bin_start+pv.get('byteOffset',0)+pa.get('byteOffset',0);stride=pv.get('byteStride',12)
  points=[struct.unpack_from('<fff',raw,start+i*stride) for i in range(pa['count'])]
  assert all(math.isfinite(v) for p in points for v in p);finite_vertex_count+=len(points)
  ia=g['accessors'][primitive['indices']];iv=g['bufferViews'][ia['bufferView']]
  st=bin_start+iv.get('byteOffset',0)+ia.get('byteOffset',0);fmt={5121:'B',5123:'H',5125:'I'}[ia['componentType']]
  indices=struct.unpack_from('<'+fmt*ia['count'],raw,st);assert max(indices)<len(points)
  for i in range(0,len(indices),3):
   aa,bb,cc=[points[indices[i+j]] for j in range(3)]
   u=[bb[j]-aa[j] for j in range(3)];v=[cc[j]-aa[j] for j in range(3)]
   cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   if sum(n*n for n in cross)<1e-20:degenerate_count+=1
assert degenerate_count==0, 'Degenerate exported triangles require cleanup'
report.update({'binary_vertex_positions_checked':finite_vertex_count,'degenerate_triangles':degenerate_count,'index_bounds':'PASS'})
print(json.dumps(report,indent=2));path.with_name('validation.json').write_text(json.dumps(report,indent=2))
