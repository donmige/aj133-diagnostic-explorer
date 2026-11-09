"""AJ133 NA exterior study. Run with Blender 4.3+: blender -b -t 4 -P reconstruct.py -- --out DIR.
No production viewer integration. All dimensions are visual estimates in metres, not measured CAD.
"""
import bpy, bmesh, math, json, sys, argparse
from pathlib import Path
from mathutils import Vector
args=argparse.ArgumentParser();args.add_argument('--out',required=True);args.add_argument('--render',action='store_true')
a=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=Path(a.out);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):bpy.data.materials.remove(block)
# Authoring coordinates: (vehicle right, height, vehicle rear). glTF: +X right,+Y up,+Z rear.
def V(p):return Vector((p[0],-p[2],p[1]))
def material(name,color,metal=.0,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
 return m
mats={
 'cast':material('Cast aluminium / approximate finish',(.34,.39,.41),.72,.38),
 'machined':material('Machined sealing edge',(.62,.68,.7),.8,.28),
 'cover':material('Composite cam covers',(.045,.065,.073),.08,.36),
 'intake':material('NA composite intake',(.075,.095,.105),.05,.42),
 'iron':material('Exhaust heat-aged metal',(.25,.17,.12),.67,.56),
 'shield':material('Formed heat shield',(.43,.46,.43),.78,.3),
 'seal':material('Sealing interfaces / emphasis',(.13,.2,.22),.12,.53),
 'rubber':material('Breather hose',(.026,.034,.04),.0,.58),
 'placeholder':material('Unverified transmission envelope',(.14,.21,.27),.3,.6),
 'amber':material('UNVERIFIED region / non physical',(.95,.5,.15),.0,.55),
}
ASSEMBLIES={};objects=[];feature_records=[]
root=bpy.data.objects.new('AJ133_NA_EXTERIOR_STUDY_R01',None);bpy.context.collection.objects.link(root)
root['geometry_status']='REFERENCE_BASED_APPROXIMATE';root['dimension_status']='UNMEASURED_ESTIMATES';root['model_variant']='L320 5.0 NA / exact 2012 VIN and revisions unconfirmed';root['no_service_clearance_claim']=True
specs=[('Block','Block',(0,0,0)),('Head_LH','Cylinder heads',(-.13,.11,0)),('Head_RH','Cylinder heads',(.13,.11,0)),('Cover_LH','Valve covers',(-.2,.23,0)),('Cover_RH','Valve covers',(.2,.23,0)),('HeadGasket_LH','Cylinder heads',(-.08,.07,0)),('HeadGasket_RH','Cylinder heads',(.08,.07,0)),('Intake_NA','Intake manifold',(0,.34,0)),('Cooler_Valley','Oil cooler',(0,.17,0)),('Cooler_Gasket','Oil cooler',(0,.13,0)),('Exhaust_LH','Exhaust & shields',(-.21,0,0)),('Exhaust_RH','Exhaust & shields',(.21,0,0)),('Shield_LH','Exhaust & shields',(-.3,.03,0)),('Shield_RH','Exhaust & shields',(.3,.03,0)),('RearFace','Rear face',(0,0,.11)),('RearSealCarrier','Rear face',(0,0,.16)),('Bellhousing_Envelope','Bellhousing',(0,0,.29)),('Sump_L320','Oil pan',(0,-.2,0)),('FrontCover','Block',(0,0,-.12))]
for key,ui,explode in specs:
 g=bpy.data.objects.new(key,None);bpy.context.collection.objects.link(g);g.parent=root;g['assembly_key']=ui;g['explode_vector_gltf']=list(explode);g['geometry_status']='APPROXIMATE';ASSEMBLIES[key]=g

def finish(ob,name,group,mat,bevel=0):
 ob.name=name;ob.parent=ASSEMBLIES[group];ob.data.materials.append(mats[mat]);
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['feature_id']=group;ob['geometry_status']='APPROXIMATE';objects.append(ob)
 if bevel:
  mod=ob.modifiers.new('Small casting edge radii (estimated)','BEVEL');mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in ob.data.polygons:p.use_smooth=len(p.vertices)<=4
 return ob

def mesh(name,verts,faces,group,mat,bevel=.0015):
 me=bpy.data.meshes.new(name);me.from_pydata([V(p) for p in verts],[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return finish(ob,name,group,mat,bevel)

def box(name,center,size,group,mat,bevel=.004):
 x,y,z=center;w,h,l=[v/2 for v in size]
 verts=[(x+dx*w,y+dy*h,z+dz*l) for dz in [-1,1] for dy in [-1,1] for dx in [-1,1]]
 return mesh(name,verts,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],group,mat,bevel)

def loft(name,sections,group,mat,bevel=.002):
 # sections are rings in engine coordinates, same vertex count, ordered consistently.
 n=len(sections[0]);verts=[p for section in sections for p in section];faces=[tuple(reversed(range(n))),tuple((len(sections)-1)*n+i for i in range(n))]
 for s in range(len(sections)-1):
  for i in range(n):faces.append((s*n+i,s*n+(i+1)%n,(s+1)*n+(i+1)%n,(s+1)*n+i))
 return mesh(name,verts,faces,group,mat,bevel)

def tube(name,pts,radius,group,mat,sides=12):
 # A low-poly swept exterior, not a fluid passage claim.
 points=[Vector(p) for p in pts]
 if len(points)>2:
  smooth=[]
  for k in range(len(points)-1):
   p0=points[max(0,k-1)];p1=points[k];p2=points[k+1];p3=points[min(k+2,len(points)-1)]
   for step in range(5):
    t=step/5;smooth.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
  points=smooth+[points[-1]]
 rings=[]
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();helper=Vector((0,1,0))
  if abs(tangent.dot(helper))>.9:helper=Vector((1,0,0))
  u=tangent.cross(helper).normalized();v=tangent.cross(u).normalized()
  rings.append([tuple(p+radius*(math.cos(j*2*math.pi/sides)*u+math.sin(j*2*math.pi/sides)*v)) for j in range(sides)])
 return loft(name,rings,group,mat,0)

def disc(name,c,r,depth,axis,group,mat,sides=40):
 unit=Vector(axis).normalized();c=Vector(c);return tube(name,[tuple(c-unit*depth/2),tuple(c+unit*depth/2)],r,group,mat,sides)

def ring(name,c,outer,inner,axis,group,mat,segments=48):
 axis=Vector(axis).normalized();helper=Vector((0,1,0)) if abs(axis.y)<.9 else Vector((1,0,0));u=axis.cross(helper).normalized();v=axis.cross(u).normalized();c=Vector(c)
 verts=[]
 for r in [outer,inner]:
  for j in range(segments):verts.append(tuple(c+r*(math.cos(j*2*math.pi/segments)*u+math.sin(j*2*math.pi/segments)*v)))
 return mesh(name,verts,[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)],group,mat,0)

# Block: deep skirt body with separate V-bank walls and external reinforcement language.
profile=[(-.205,-.19),(.205,-.19),(.23,-.11),(.23,.045),(.17,.11),(-.17,.11),(-.23,.045),(-.23,-.11)]
loft('Deep skirt casting', [[(x,y,z) for x,y in profile] for z in [-.295,.28]],'Block','cast',.008)
for side in [-1,1]:
 sections=[]
 for z in [-.29,.28]:sections.append([(side*x,y,z) for x,y in [(.075,.035),(.205,-.04),(.30,.11),(.11,.30),(.085,.20)]])
 loft('V-bank exterior '+str(side),sections,'Block','cast',.005)
 for j,z in enumerate([-.23,-.09,.06,.20]):
  tube('External rib / approximate '+str(side)+' '+str(j),[(side*.218,-.15,z),(side*.255,.015,z),(side*.32,.11,z+.017)],.009,'Block','cast',6)
 # deliberately no small holes, bolt heads, casting plugs or gallery drillings

# Valley well is a shallow visible surface, no claimed drains.
box('Valley floor / no inferred drains',(0,.085,-.005),(.20,.025,.51),'Block','cast',.009)
# Land Rover deep sump visual envelope, no differential mounting claim.
sump_profile=[(-.20,-.19),(.20,-.19),(.195,-.27),(.15,-.34),(-.15,-.34),(-.20,-.30)]
loft('Deep single-piece sump envelope',[[(x,y,z) for x,y in sump_profile] for z in [-.285,.28]],'Sump_L320','cast',.009)
for side in [-1,1]:
 for z in [-.22,-.1,.02,.14,.23]:tube('Sump reinforcement '+str(side)+str(z),[(side*.20,-.205,z),(side*.185,-.28,z)],.007,'Sump_L320','cast',6)
box('Block sump sealing edge',(0,-.19,0),(.425,.007,.574),'Sump_L320','seal',.003)

# Head & cover cross sections, separate bank identities. Positions and depths estimated.
for side,bank in [(-1,'LH'),(1,'RH')]:
 n=Vector((side*.70710678,.70710678,0));u=Vector((side*.70710678,-.70710678,0));base=Vector((side*.205,.205,0));length=.56
 def local(w,h,z):return tuple(base+w*u+h*n+Vector((0,0,z)))
 head_profile=[(-.125,.006),(.125,.006),(.125,.105),(.105,.145),(-.102,.145),(-.125,.115)]
 loft(bank+' bank-specific head casting',[[local(w,h,z) for w,h in head_profile] for z in [-.3,length/2]],'Head_'+bank,'cast',.004)
 # Machined deck and gasket shown as narrow exterior flange, not detailed gasket holes.
 for z in [-.30,.28]:tube(bank+' visible gasket end', [local(-.129,.002,z),local(.129,.002,z)],.002,'HeadGasket_'+bank,'seal',6)
 for w in [-.129,.129]:tube(bank+' visible gasket long edge',[local(w,.002,-.30),local(w,.002,.28)],.002,'HeadGasket_'+bank,'seal',6)
 # cast side lobes supporting the exhaust interface, four-cylinder relationship only.
 for j,z in enumerate([-.225,-.075,.075,.225]):
  box(bank+' exhaust-side casting lobe '+str(j),(side*.345,.235,z),(.055,.07,.10),'Head_'+bank,'cast',.012)
 # cover irregular section and front/rear scalloping silhouette
 cover_profile=[(-.135,.15),(.135,.15),(.138,.186),(.11,.23),(.06,.255),(-.09,.255),(-.135,.22)]
 rings=[]
 for z,taper in [(-.32,.85),(-.28,1),(.24,1),(.29,.86)]:rings.append([local(w*taper,h,z) for w,h in cover_profile])
 loft(bank+' composite camshaft cover',rings,'Cover_'+bank,'cover',.004)
 for w in [-.137,.137]:tube(bank+' cover gasket edge',[local(w,.151,-.29),local(w,.151,.27)],.003,'Cover_'+bank,'seal',8)
 for j,z in enumerate([-.22,-.12,-.02,.08,.18]):
  tube(bank+' molded cover rib '+str(j),[local(-.12,.22,z),local(-.07,.256,z),local(.065,.256,z),local(.12,.22,z)],.003,'Cover_'+bank,'cover',6)
 # coil trim covers visible over top; no fabricated fastener positions
 loft(bank+' ignition trim shell',[[local(w,h,z) for w,h in [(-.075,.257),(.075,.257),(.06,.276),(-.065,.276)]] for z in [-.26,.24]],'Cover_'+bank,'intake',.003)
 # RH cover contains twin integrated PCV caps; not one cap on each bank.
 if side==1:
  for j,z in enumerate([-.21,-.105]):
   c=local(-.09,.268,z);disc('RH PCV cap '+str(j+1),c,.036,.018,n,'Cover_RH','cover',40)
   ring('RH PCV cap molded rim '+str(j+1),tuple(Vector(c)+n*.01),.031,.027,n,'Cover_RH','machined',32)
 else:
  c=local(.015,.29,-.19);disc('Oil filler cap (LH)',c,.033,.025,n,'Cover_LH','cover',36)
 # rear head surface remains unperforated: ball-style plug identity unresolved.

# Valley oil cooler: plate stack, sealing layer, exterior hose spigots only.
box('Valley cooler gasket / approximate outline',(0,.114,-.005),(.185,.006,.40),'Cooler_Gasket','seal',.01)
box('Plate cooler body',(0,.145,-.005),(.17,.055,.385),'Cooler_Valley','machined',.012)
for j in range(7):box('Cooler plate '+str(j),(0,.121+j*.007,-.005),(.177,.0015,.39),'Cooler_Valley','cast',.008)
tube('Cooler visible union envelope',[(-.075,.135,-.18),(-.12,.135,-.19),(-.12,.14,-.23)],.017,'Cooler_Valley','cast',16)

# NA intake central plenum and eight broad external runner forms, no supercharger.
box('NA intake central chamber',(0,.39,.015),(.165,.135,.46),'Intake_NA','intake',.035)
for side in [-1,1]:
 for j,z in enumerate([-.21,-.07,.07,.21]):
  # asymmetry is a visual interpretation of overlapping runner envelope, not exact channels
  lead=z+(.013 if side==1 else -.013)
  tube('NA external runner '+str(side)+' '+str(j),[(side*.03,.43,lead),(side*.09,.455,lead),(side*.15,.44,lead+.012),(side*.19,.37,z),(side*.22,.30,z)],.041,'Intake_NA','intake',16)
  box('NA intake lower flange '+str(side)+str(j),(side*.205,.295,z),(.06,.018,.09),'Intake_NA','cover',.005)
disc('NA throttle body envelope',(0,.335,-.32),.06,.085,(0,0,1),'Intake_NA','cast',40)
ring('Throttle mouth',(0,.335,-.366),.06,.047,(0,0,1),'Intake_NA','machined',40)
disc('Throttle mouth dark recess',(0,.335,-.364),.046,.002,(0,0,1),'Intake_NA','rubber',32)
# Rear VIS actuator silhouette, approximate envelope only.
for side in [-1,1]:disc('NA rear VIS actuator '+str(side),(side*.09,.385,.29),.028,.035,(0,0,1),'Intake_NA','cover',24)
# Front top-access oil filter housing envelope; no service clearance claim.
disc('Oil filter housing visual envelope',(-.12,.28,-.3),.049,.13,(0,1,0),'Block','cast',32)
disc('Oil filter cap',(-.12,.352,-.3),.05,.023,(0,1,0),'Block','cover',32)
# PCV external hoses: approximate curves between identifiable regions; fluid direction not asserted.
tube('RH part-load breather / curve approximate',[(.20,.49,-.20),(.16,.52,-.22),(.11,.54,-.12),(.07,.52,-.05),(0,.49,-.10)],.011,'Cover_RH','rubber',12)
tube('Full-load external breather / approximate', [(-.28,.42,-.24),(-.29,.46,-.30),(-.25,.48,-.37),(-.15,.42,-.38)],.012,'Cover_LH','rubber',12)

# Asymmetric exhaust manifold envelopes: short runners merge into bank-specific collectors.
for side,bank in [(-1,'LH'),(1,'RH')]:
 zs=[-.225,-.075,.075,.225]
 for j,z in enumerate(zs):
  dest=z*.8+(.03 if side<0 else 0)
  tube(bank+' manifold runner '+str(j),[(side*.35,.23,z),(side*.405,.205,z),(side*.45,.145,dest),(side*.46,.095,dest+.025)],.025,'Exhaust_'+bank,'iron',14)
 collector_pts=[(side*.46,.095,-.21),(side*(.47 if side<0 else .46),.085,-.08),(side*.47,.07,.08),(side*.45,.045,.24),(side*.42,.01,.31)]
 tube(bank+' merged collector',collector_pts,.038 if side<0 else .035,'Exhaust_'+bank,'iron',18)
 ring(bank+' outlet flange',(side*.42,.005,.325),.049,.026,(0,0,1),'Exhaust_'+bank,'machined',32)
 # thin formed shield, varying bank-specific profile; hides manifold as actual exterior context would
 sections=[]
 for j,z in enumerate([-.28,-.18,0,.18,.29]):
  widen=[.0,.025,.038,.028,-.005][j]
  h=.17+(.01 if bank=='LH' else -.012)
  sections.append([(side*(.405+widen),h+.095,z),(side*(.49+widen),h+.07,z),(side*(.505+widen),h-.055,z),(side*(.495+widen),h-.06,z),(side*(.48+widen),h+.06,z),(side*(.405+widen),h+.087,z)])
 loft(bank+' formed outer heat shield',sections,'Shield_'+bank,'shield',.002)
 tube(bank+' shield stiffening bead',[(side*.50,.24,-.2),(side*.54,.24,0),(side*.525,.22,.21)],.003,'Shield_'+bank,'shield',8)

# Rear face casting silhouette and separate seal carrier. NO gallery plug meshes.
rear_outline=[(-.22,-.185),(.22,-.185),(.26,-.12),(.25,.10),(.15,.22),(0,.12),(-.15,.22),(-.25,.10),(-.26,-.12)]
loft('Rear block casting face', [[(x,y,z) for x,y in rear_outline] for z in [.278,.293]],'RearFace','cast',.003)
carrier_outline=[(-.14,-.17),(.14,-.17),(.175,-.095),(.16,.015),(.11,.085),(.045,.105),(-.06,.10),(-.14,.05),(-.17,-.08)]
carrier=loft('Rear seal carrier / revision unconfirmed',[[(x,y,z) for x,y in carrier_outline] for z in [.296,.312]],'RearSealCarrier','cast',.003)
# central seal opening is a known crankshaft interface; not an oil gallery or rotating internals
cutter=disc('TEMP seal opening',(0,-.055,.305),.073,.1,(0,0,1),'RearSealCarrier','cast',48)
bpy.context.view_layer.objects.active=carrier;mod=carrier.modifiers.new('Known central seal aperture','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=mod.name);objects.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
ring('Rear crankshaft seal zone',(0,-.055,.314),.078,.069,(0,0,1),'RearSealCarrier','seal',48)
# approximate rib language, deliberately no invented fastener pattern
for side in [-1,1]:tube('Rear carrier stiffening feature '+str(side),[(side*.09,-.14,.315),(side*.13,-.07,.315),(side*.1,.025,.315)],.005,'RearSealCarrier','cast',6)

# Front timing cover visual envelope, structural context without pulley detail.
front_profile=[(-.23,-.16),(.23,-.16),(.26,.05),(.19,.25),(.08,.29),(0,.17),(-.1,.29),(-.23,.21)]
loft('Front timing cover envelope',[[(x,y,z) for x,y in front_profile] for z in [-.32,-.295]],'FrontCover','cast',.005)
disc('Front accessory pulley envelope',(0,-.06,-.352),.095,.05,(0,0,1),'FrontCover','cover',48)
ring('Pulley face rim',(0,-.06,-.38),.089,.068,(0,0,1),'FrontCover','cast',40)

# Open bellhousing shell: context ONLY. Not a verified gearbox casting or access opening.
rings=[]
for rear,r in [(.33,.29),(.36,.29),(.55,.205),(.62,.18)]:
 rings.append([(r*math.cos(i*2*math.pi/48),-.055+r*math.sin(i*2*math.pi/48),rear) for i in range(48)])
# surface shell using custom faces without front/end caps
verts=[p for r in rings for p in r];faces=[]
for j in range(len(rings)-1):
 for i in range(48):faces.append((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i))
mesh('Bellhousing UNVERIFIED clearance envelope',verts,faces,'Bellhousing_Envelope','placeholder',0)
ASSEMBLIES['Bellhousing_Envelope']['geometry_status']='UNVERIFIED_ENVELOPE';ASSEMBLIES['Bellhousing_Envelope']['not_for_access_planning']=True

# Named diagnostic anchor empties. Unverified plug regions deliberately carry no physical geometry.
anchors=[('gallery','RearFace',(-.09,.09,.30),'UNVERIFIED_REGION'),('head-plugs','Head_RH',(.25,.32,.28),'UNVERIFIED_REGION'),('head-gasket','HeadGasket_LH',(-.29,.12,.05),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('valve-cover','Cover_LH',(-.35,.26,-.05),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('pcv','Cover_RH',(.22,.47,-.15),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('cooler','Cooler_Valley',(0,.18,-.02),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('vacuum','RearFace',(.22,.15,.3),'UNVERIFIED_REGION'),('cam','Head_RH',(.3,.30,-.2),'UNVERIFIED_REGION'),('valley','Block',(0,.09,.12),'ILLUSTRATIVE_REGION'),('exhaust','Exhaust_LH',(-.46,.12,.1),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('rear-main','RearSealCarrier',(0,-.055,.318),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('bellhousing','Bellhousing_Envelope',(0,-.34,.34),'ILLUSTRATIVE_REGION')]
for ident,group,pos,status in anchors:
 ob=bpy.data.objects.new('anchor__'+ident,None);bpy.context.collection.objects.link(ob);ob.parent=ASSEMBLIES[group];ob.location=V(pos);ob.empty_display_size=.02;ob['diagnostic_id']=ident;ob['evidence_status']=status;ob['physical_feature']=False
# Source/identity metadata for all component groups.
sources={'block':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43093/brand/land-rover/','head':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43096/brand/land-rover/','cover':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53055.43171/brand/land-rover/','cooler':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53047.43113/brand/land-rover/','exhaust':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43102/brand/land-rover/','intake':'https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43099/brand/land-rover/','manual':'https://www.billswebspace.com/5.0V8.pdf'}
for key,g in ASSEMBLIES.items():
 source='block'
 if key.startswith('Head'):source='head'
 elif key.startswith('Cover'):source='cover'
 elif key.startswith('Cooler'):source='cooler'
 elif key.startswith(('Exhaust','Shield')):source='exhaust'
 elif key=='Intake_NA':source='intake'
 elif key in ['Sump_L320','FrontCover','Bellhousing_Envelope']:source='manual'
 g['source_url']=sources[source];g['fitment_status']='2012 vehicle VIN/engine revisions not verified';g['fluid_connection_status']='NOT_MODELED'
 feature_records.append({'node':key,'ui_assembly':g['assembly_key'],'geometry_status':g['geometry_status'],'source_url':sources[source],'dimensions':'visual estimates','explode_vector_gltf':list(g['explode_vector_gltf'])})
# Join within component+material to keep draw calls low; preserve source per group and anchors.
for key,g in ASSEMBLIES.items():
 for mat in list(mats.values()):
  group=[o for o in list(g.children) if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
  if not group:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in group:ob.select_set(True)
  bpy.context.view_layer.objects.active=group[0]
  if len(group)>1:bpy.ops.object.join()
  ob=bpy.context.object;ob.name=key+'__'+mat.name.split(' /')[0].replace(' ','_');ob['geometry_status']='APPROXIMATE' if key!='Bellhousing_Envelope' else 'UNVERIFIED_ENVELOPE'
# Set geometry origins to common datum; component-local anchors can inherit future group transforms.
# Group origins all at model origin: no hidden or unmeasured mechanical pivot is implied.
bpy.ops.object.select_all(action='DESELECT')
for ob in [root]+list(root.children_recursive):ob.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/'aj133-na-exterior-r01.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
manifest={'version':'phase2-r01','approval_scope':'separate model study only; not integrated or deployed','variant':'2012 L320 AJ133 5.0 naturally aspirated target; VIN/revisions unconfirmed','axes':'GLTF +X vehicle right, +Y up, +Z rear','units':'metres, estimated scale; NOT measured CAD','sources':sources,'assemblies':feature_records,'diagnostic_anchors':[{'id':i,'node':'anchor__'+i,'parent':g,'position_gltf':list(p),'status':s,'physical_geometry':False} for i,g,p,s in anchors],'unresolved':['Rear block oil-gallery plug identity, position and oil connections','Rear cylinder-head ball-plug identities, positions and passage connections','Exact casting/cover/carrier revisions','Installed chassis/firewall/gearbox clearances','Valley drains and actual oil migration','Exact PCV hose curves and hidden separator geometry'],'excluded':['internal rotating engine parts','invented gallery or manufacturing plug meshes','unverified holes or fastener patterns','validated service routes'],'performance_targets':{'glb_megabytes_max':8,'triangles_max':180000,'draw_calls_target_max':60}}
manifest['evidence_facts']=[
 {'id':'F01','feature':'Valley oil cooler and separate gasket','identity':'verified in NA catalogue drawing','geometry':'approximate silhouette, scale and flange outline','source':'cooler','drawing':'P0190565-02','callouts':['6A642','6L621']},
 {'id':'F02','feature':'RH cam cover twin PCV caps','identity':'verified in cover drawing and NA training illustration','geometry':'estimated cap diameters/centres and hose curves','source':'cover','drawing':'P0190624-05','callouts':['6582A','13B802'],'manual_printed_page':'3-32','manual_pdf_page':116},
 {'id':'F03','feature':'Separate LH and RH exhaust manifolds/shields','identity':'verified bank-specific catalogue assemblies','geometry':'estimated profiles, runner trajectories, thickness and shield clearance','source':'exhaust','drawing':'P0190562-03','callouts':['9430A','9430B','9A462A','9A462B']},
 {'id':'F04','feature':'Cylinder heads and external gasket interface','identity':'verified component/interface','geometry':'estimated bank-specific casting shell; rear-face small details omitted','source':'head','drawing':'P0190560-04','callouts':['6049','6051']},
 {'id':'F05','feature':'NA variable intake architecture','identity':'verified NA system architecture','geometry':'runner/plenum shapes and actuator sizes estimated','source':'intake','manual_printed_page':'2-12','manual_pdf_page':36},
 {'id':'F06','feature':'Rear crankshaft seal carrier','identity':'verified carrier/interface, revision NOT selected','geometry':'generic interpretation; not either measured catalogue revision','source':'block','drawing':'P0190547-07','callouts':['6K301A','6K301B']},
 {'id':'F07','feature':'Rear block oil-gallery and rear head ball-style plugs','identity':'UNRESOLVED; no oil-passage connection established','geometry':'NONE; anchor regions only','source':'block','note':'Catalogue plug callouts do not establish fluid function; no plug copied into geometry.'},
 {'id':'F08','feature':'Bellhousing, vacuum pump and cam sensor anchors','identity':'specific geometry/locations unverified','geometry':'bellhousing envelope only; pump/sensor physical meshes omitted','source':'manual','note':'No service-access or clearance inference.'}
]
manifest['review_gates']=['Separate model render review before any viewer replacement','Confirm VIN/engine serial and revision-specific features','Confirm plug identity before converting regional marker into a physical feature','Review measured clearances before any validated inspection route']
(OUT/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2))
# Review studio, excluded from GLB export above.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=1000;scene.render.resolution_y=750;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
# Ground and studio lights.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.37));floor=bpy.context.object;floor.name='REVIEW_STUDIO / excluded from GLB';floor.data.materials.append(material('Studio ground',(.025,.037,.047),.0,.6))
def area(name,pos,power,size):
 bpy.ops.object.light_add(type='AREA',location=V(pos));light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(V((0,.12,0))-light.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-1.5,2,-1),90,2);area('Rear rim',(1.5,1.6,1.7),120,1.8);area('Fill',(1,1,-1.8),65,1.5)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Review orthographic camera';cam.data.type='ORTHO';cam.data.ortho_scale=1.65;scene.camera=cam
views={'assembled':(-1.25,1.1,-1.5),'rear':(.85,.7,1.65),'top':(0,2,.001),'left':(-2,.35,0),'valley':(-.7,1.3,-.9),'rear-exposed':(.55,.45,1.8),'exploded':(-1.1,1.1,-1.5)}
# Save assembled editable source, with camera and studio kept outside engine root.
cam.location=V(views['assembled']);cam.rotation_euler=(V((0,.10,.08))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'aj133-na-exterior-r01.blend'))
def hide_group(key):
 for ob in [ASSEMBLIES[key]]+list(ASSEMBLIES[key].children_recursive):ob.hide_render=True

if a.render:
 for view,position in views.items():
  for g in ASSEMBLIES.values():
   g.location=(0,0,0)
   for ob in [g]+list(g.children_recursive):ob.hide_render=False
  if view in ['valley','rear-exposed']:hide_group('Bellhousing_Envelope')
  if view=='valley':
   hide_group('Intake_NA')
  if view=='rear-exposed':
   hide_group('Shield_LH');hide_group('Shield_RH')
  if view=='exploded':
   for g in ASSEMBLIES.values():g.location=V(g['explode_vector_gltf'])
  cam.data.ortho_scale=1.85 if view=='exploded' else 1.65
  cam.location=V(position);cam.rotation_euler=(V((0,.10,.08))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(view+'.png'));bpy.ops.render.render(write_still=True)
print('AJ133 separate reconstruction exported:',OUT)
