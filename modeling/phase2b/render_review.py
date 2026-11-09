"""Render physical review views from Phase 2B source; never writes the source .blend."""
import bpy,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out)
scene=bpy.context.scene;cam=scene.camera;root=bpy.data.objects['AJ133_NA_PHASE2B_R01'];groups={o.name:o for o in root.children if 'assembly_key' in o}
original={o:tuple(o.data.materials) for o in root.children_recursive if o.type=='MESH'}
diag=bpy.data.collections.get('DIAGNOSTIC_OVERLAYS / NON PHYSICAL');overlay_objs=list(diag.objects) if diag else []
def V(p):return Vector((p[0],-p[2],p[1]))
def hidden(key,value):
 g=groups[key]
 for ob in [g]+list(g.children_recursive):ob.hide_render=value

def reset():
 for key,g in groups.items():hidden(key,False);g.location=(0,0,0)
 for ob,mats in original.items():ob.data.materials.clear();[ob.data.materials.append(m) for m in mats]
 for ob in overlay_objs:ob.hide_render=True

def ghost(keys):
 for key in keys:
  for ob in groups[key].children_recursive:
   if ob.type!='MESH':continue
   for slot in ob.material_slots:
    m=slot.material.copy();m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.19;slot.material=m

views=[
 ('rear-engine-hires',(0,.36,1.8),(0,.12,.28),1.35,'rear'),
 ('left-exhaust',(-1.8,.3,0),(0,.12,.05),1.4,'side'),
 ('right-exhaust',(1.8,.3,0),(0,.12,.05),1.4,'side'),
 ('rear-heads-isolated',(0,.42,1.1),(0,.28,.275),.85,'heads'),
 ('rear-block-isolated',(.32,.20,1.3),(0,.025,.30),.92,'block'),
 ('left-transparent',(-1.8,.3,.10),(0,.12,.08),1.4,'ghost'),
 ('right-transparent',(1.8,.3,.10),(0,.12,.08),1.4,'ghost'),
]
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_percentage=100
for name,pos,target,scale,mode in views:
 reset();hidden('Bellhousing_Envelope',True)
 if mode in ['side','ghost']:
  hidden('Shield_LH',True);hidden('Shield_RH',True)
 if mode=='heads':
  for key in groups:hidden(key,key not in ['Head_LH','Head_RH','HeadGasket_LH','HeadGasket_RH'])
 if mode=='block':
  for key in groups:hidden(key,key not in ['Block','RearFace','RearSealCarrier','Sump_L320'])
 if mode=='ghost':ghost(['Head_LH','Head_RH','Block','RearFace','RearSealCarrier'])
 scene.render.resolution_x=2000 if mode=='rear' else 1600;scene.render.resolution_y=1500 if mode=='rear' else 1200
 cam.location=V(pos);cam.rotation_euler=(V(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
# Same-camera before/after, from the unchanged fallback source.
bpy.ops.wm.open_mainfile(filepath=str(out/'fallback-phase2/aj133-na-exterior-r01.blend'))
scene=bpy.context.scene;cam=scene.camera;g=bpy.data.objects['Bellhousing_Envelope']
for ob in [g]+list(g.children_recursive):ob.hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=2000;scene.render.resolution_y=1500;scene.render.resolution_percentage=100
cam.location=V((0,.36,1.8));cam.rotation_euler=(V((0,.12,.28))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.35;scene.render.filepath=str(out/'phase2-baseline-same-camera.png');bpy.ops.render.render(write_still=True)
print('Phase 2B physical review renders and same-camera baseline complete')
