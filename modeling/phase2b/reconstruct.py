"""AJ133 NA Phase 2B rear/exhaust refinement study. Run with Blender 4.3+: blender -b -t 4 -P reconstruct.py -- --out DIR.
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
root=bpy.data.objects.new('AJ133_NA_PHASE2B_R01',None);bpy.context.collection.objects.link(root)
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
 rings=[];previous_u=None
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();helper=Vector((0,1,0))
  if abs(tangent.dot(helper))>.9:helper=Vector((1,0,0))
  u=tangent.cross(helper).normalized() if previous_u is None else (previous_u-tangent*previous_u.dot(tangent)).normalized()
  if u.length<.1:u=tangent.cross(helper).normalized()
  v=tangent.cross(u).normalized();previous_u=u
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
 head_profile=[(-.125,.006),(.125,.006),(.136,.045),(.136,.105),(.111,.146),(.07,.158),(-.075,.158),(-.115,.143),(-.134,.105),(-.134,.05)]
 # Multi-section rear shoulder: visible exterior envelope only, not recovered CAD.
 head_sections=[]
 for z,taper in [(-.30,.96),(-.27,1),(.18,1),(.245,.99),(.285,.94),(.308,.91)]:
  head_sections.append([local(w*taper,h,z) for w,h in head_profile])
 loft(bank+' rear-shouldered head / contours estimated',head_sections,'Head_'+bank,'cast',.003)
 # NA rear CPS actuator component is identified by manual 3-4 (PDF 88).
 # Its envelope and mounting centre here are estimates, NOT a gallery plug.
 cps=local(.075,.087,.338)
 disc(bank+' NA CPS solenoid envelope / not a plug',cps,.023,.055,(0,0,1),'Head_'+bank,'cover',32)
 box(bank+' CPS electrical connector / approximate',tuple(Vector(cps)+Vector((side*.027,.008,.018))),(.038,.023,.027),'Head_'+bank,'cover',.003)

 # Machined deck and gasket shown as narrow exterior flange, not detailed gasket holes.
 for z in [-.30,.29]:tube(bank+' visible gasket end', [local(-.129,.002,z),local(.129,.002,z)],.002,'HeadGasket_'+bank,'seal',6)
 for w in [-.129,.129]:tube(bank+' visible gasket long edge',[local(w,.002,-.30),local(w,.002,.29)],.002,'HeadGasket_'+bank,'seal',6)
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

# NA manifold flange and collector relationships follow P0190562-03;
# every depth, clearance and radius remains estimated. No bolt holes are invented.
for side,bank in [(-1,'LH'),(1,'RH')]:
 zs=[-.225,-.075,.075,.225]
 # Continuous four-port mounting land, with rounded external shoulders only.
 flange=[(.181,-.285),(.254,-.285),(.275,-.25),(.277,.24),(.253,.285),(.181,.285),(.167,.25),(.167,-.25)]
 loft(bank+' manifold mounting flange / no invented holes',[[(side*x,y,z) for y,z in flange] for x in [.348,.363]],'Exhaust_'+bank,'machined',.003)
 for j,z in enumerate(zs):
  dest=z*.79+(.012 if side<0 else -.008)
  pts=[(side*.36,.223,z),(side*.388,.218,z),(side*.423,.19,z+.014),(side*.449,.145,dest),(side*.455,.115,dest+.018)]
  tube(bank+' manifold runner envelope '+str(j),pts,.023 if bank=='LH' else .024,'Exhaust_'+bank,'iron',18)
 # Cast outer envelope and rearward/downward outlet; not fluid simulation.
 collector=[(side*.447,.115,-.245),(side*.461,.102,-.14),(side*.465,.093,0),(side*.459,.08,.15),(side*.439,.052,.255),(side*.417,.005,.315)]
 tube(bank+' collector / estimated profile',collector,.037 if bank=='LH' else .035,'Exhaust_'+bank,'iron',24)
 ring(bank+' manifold outlet flange',(side*.417,-.002,.328),.049,.027,(0,0,1),'Exhaust_'+bank,'machined',40)
 # Contoured thin shield with rolled borders. No shield fixing centres claimed.
 sections=[]
 for j,z in enumerate([-.29,-.23,-.12,.02,.16,.26,.305]):
  bulge=[-.006,.012,.032,.039,.033,.012,-.008][j]
  top=.285+(.009 if bank=='LH' else -.005)
  sections.append([(side*(.365+bulge),top,z),(side*(.420+bulge),top+.012,z),(side*(.48+bulge),top-.005,z),(side*(.501+bulge),top-.065,z),(side*(.497+bulge),top-.12,z),(side*(.491+bulge),top-.123,z),(side*(.492+bulge),top-.065,z),(side*(.473+bulge),top-.013,z),(side*(.420+bulge),top+.003,z),(side*(.365+bulge),top-.006,z)])
 loft(bank+' formed heat-shield envelope',sections,'Shield_'+bank,'shield',.0015)
 tube(bank+' rolled shield upper lip',[(side*.365,.285,-.27),(side*.397,.30,-.12),(side*.404,.30,.08),(side*.377,.285,.28)],.003,'Shield_'+bank,'shield',10)

# Rear face casting silhouette and separate seal carrier. NO gallery plug meshes.
rear_outline=[(-.235,-.185),(.235,-.185),(.26,-.13),(.275,-.055),(.265,.10),(.245,.135),(.195,.21),(.135,.242),(.095,.19),(.07,.135),(-.07,.135),(-.095,.19),(-.135,.242),(-.195,.21),(-.245,.135),(-.265,.10),(-.275,-.055),(-.26,-.13)]
loft('Rear block stepped casting envelope', [[(x,y,z) for x,y in rear_outline] for z in [.279,.302]],'RearFace','cast',.003)
# A visible interface rim, not a measured bolt pattern or service opening.
tube('Rear block to bellhousing flange outline / estimated',[(x,y,.307) for x,y in rear_outline+[rear_outline[0]]],.004,'RearFace','machined',8)
carrier_outline=[(-.142,-.178),(.138,-.178),(.162,-.15),(.177,-.092),(.172,-.035),(.146,.025),(.113,.063),(.06,.092),(.042,.112),(-.035,.113),(-.063,.094),(-.113,.073),(-.145,.025),(-.168,-.028),(-.175,-.092),(-.159,-.145)]
carrier=loft('Rear seal carrier / traced silhouette / revision unconfirmed',[[(x,y,z) for x,y in carrier_outline] for z in [.305,.325]],'RearSealCarrier','cast',.002)
cutter=disc('TEMP known central seal aperture',(0,-.055,.32),.073,.10,(0,0,1),'RearSealCarrier','cast',64)
bpy.context.view_layer.objects.active=carrier;mod=carrier.modifiers.new('Central crankshaft seal interface only','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';bpy.ops.object.modifier_apply(modifier=mod.name);objects.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
ring('Rear main sealing interface',(0,-.055,.327),.079,.069,(0,0,1),'RearSealCarrier','seal',64)
# Broad carrier stiffening features visually guided by catalogue; no drillings.
for j,(x,y) in enumerate([(-.13,-.145),(-.15,-.04),(-.12,.035),(-.045,.088),(.05,.09),(.123,.035),(.15,-.055),(.12,-.15)]):
 dx,dy=x,y+.055;r=(dx*dx+dy*dy)**.5
 inner=(dx/r*.087,-.055+dy/r*.087,.329)
 tube('Carrier reinforcement / estimated '+str(j),[inner,(x,y,.329)],.0045,'RearSealCarrier','cast',6)
tube('Carrier perimeter sealing edge',[(x,y,.328) for x,y in carrier_outline+[carrier_outline[0]]],.002,'RearSealCarrier','seal',6)
# Actual gallery plug identity is documented; exact placement is not established.
# Leave both upper-corner alternatives unperforated and annotate as investigation regions.

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
anchors=[('gallery','RearFace',(0,.16,.33),'DOCUMENTED_SOURCE_APPROXIMATE_REGION'),('head-plugs','Head_RH',(.25,.32,.28),'UNVERIFIED_REGION'),('head-gasket','HeadGasket_LH',(-.29,.12,.05),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('valve-cover','Cover_LH',(-.35,.26,-.05),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('pcv','Cover_RH',(.22,.47,-.15),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('cooler','Cooler_Valley',(0,.18,-.02),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('vacuum','RearFace',(.22,.15,.3),'UNVERIFIED_REGION'),('cam','Head_RH',(.3,.30,-.2),'UNVERIFIED_REGION'),('valley','Block',(0,.09,.12),'ILLUSTRATIVE_REGION'),('exhaust','Exhaust_LH',(-.46,.12,.1),'VERIFIED_COMPONENT_APPROXIMATE_POSITION'),('rear-main','RearSealCarrier',(0,-.055,.318),'VERIFIED_INTERFACE_APPROXIMATE_POSITION'),('bellhousing','Bellhousing_Envelope',(0,-.34,.34),'ILLUSTRATIVE_REGION')]
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
# Remove numeric bevel/boolean slivers, not mechanically meaningful surfaces.
cleanup_count=0
def clean_mesh(ob):
 global cleanup_count
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bad=[f for f in bm.faces if f.calc_area()<1e-10]
 cleanup_count+=len(bad)
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
for ob in root.children_recursive:
 if ob.type=='MESH':clean_mesh(ob)

# Set geometry origins to common datum; component-local anchors can inherit future group transforms.
# Group origins all at model origin: no hidden or unmeasured mechanical pivot is implied.
bpy.ops.object.select_all(action='DESELECT')
for ob in [root]+list(root.children_recursive):ob.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/'aj133-na-phase2b-r01.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
manifest={'version':'phase2b-r01','approval_scope':'separate model study only; not integrated or deployed','variant':'2012 L320 AJ133 5.0 naturally aspirated target; VIN/revisions unconfirmed','axes':'GLTF +X vehicle right, +Y up, +Z rear','units':'metres, estimated scale; NOT measured CAD','sources':sources,'assemblies':feature_records,'diagnostic_anchors':[{'id':i,'node':'anchor__'+i,'parent':g,'position_gltf':list(p),'status':s,'physical_geometry':False} for i,g,p,s in anchors],'unresolved':['Exact 3D position, side, dimensions and casting revision of the documented upper rear block plug','Rear cylinder-head ball-plug identities, positions and passage connections','Exact casting/cover/carrier revisions','Installed chassis/firewall/gearbox clearances','Valley drains and actual oil migration','Exact PCV hose curves and hidden separator geometry'],'excluded':['internal rotating engine parts','invented gallery or manufacturing plug meshes','unverified holes or fastener patterns','validated service routes'],'performance_targets':{'glb_megabytes_max':8,'triangles_max':180000,'draw_calls_target_max':60}}
manifest['evidence_facts']=[
 {'id':'F01','feature':'Valley oil cooler and separate gasket','identity':'verified in NA catalogue drawing','geometry':'approximate silhouette, scale and flange outline','source':'cooler','drawing':'P0190565-02','callouts':['6A642','6L621']},
 {'id':'F02','feature':'RH cam cover twin PCV caps','identity':'verified in cover drawing and NA training illustration','geometry':'estimated cap diameters/centres and hose curves','source':'cover','drawing':'P0190624-05','callouts':['6582A','13B802'],'manual_printed_page':'3-32','manual_pdf_page':116},
 {'id':'F03','feature':'Separate LH and RH exhaust manifolds/shields','identity':'verified bank-specific catalogue assemblies','geometry':'estimated profiles, runner trajectories, thickness and shield clearance','source':'exhaust','drawing':'P0190562-03','callouts':['9430A','9430B','9A462A','9A462B']},
 {'id':'F04','feature':'Cylinder heads and external gasket interface','identity':'verified component/interface','geometry':'stepped/tapered rear exterior envelope; exact casting contours unmeasured; no ball plugs fabricated','source':'head','drawing':'P0190560-04','callouts':['6049','6051']},
 {'id':'F05','feature':'NA variable intake architecture','identity':'verified NA system architecture','geometry':'runner/plenum shapes and actuator sizes estimated','source':'intake','manual_printed_page':'2-12','manual_pdf_page':36},
 {'id':'F06','feature':'Rear crankshaft seal carrier','identity':'verified carrier/interface, revision NOT selected','geometry':'generic interpretation; not either measured catalogue revision','source':'block','drawing':'P0190547-07','callouts':['6K301A','6K301B']},
 {'id':'F07','feature':'Rear block oil-gallery and rear head ball-style plugs','identity':'Rear block source documented by SSM51477; head ball-plug identity/function unresolved','geometry':'NONE; anchor regions only','source':'block','note':'Catalogue plug callouts do not establish fluid function; no plug copied into geometry.'},
 {'id':'F08','feature':'Bellhousing, vacuum pump and cam sensor anchors','identity':'specific geometry/locations unverified','geometry':'bellhousing envelope only; pump/sensor physical meshes omitted','source':'manual','note':'No service-access or clearance inference.'}
]
manifest['review_gates']=['Separate model render review before any viewer replacement','Confirm VIN/engine serial and revision-specific features','Confirm plug identity before converting regional marker into a physical feature','Review measured clearances before any validated inspection route']
manifest['sources']['SSM51477']='https://static.nhtsa.gov/odi/tsbs/2013/MC-10072200-0699.pdf'
manifest['numerical_cleanup']={'minimum_triangle_area_m2':1e-10,'sliver_faces_removed':cleanup_count}
manifest['phase2b_refinement']={
 'baseline':'Phase 2 R01 preserved independently in fallback-phase2',
 'rear_heads':'Multi-section shoulder/rear taper, explicit gasket boundaries and NA CPS solenoid envelopes; contours and centres estimated. No ball plugs.',
 'rear_block':'Stepped rear silhouette, flange boundary and carrier outline guided by P0190547-07 and training 2-54. No physical gallery plug added.',
 'exhaust':'Continuous manifold mounting lands, transported-frame runner sweeps, cast collector envelopes and contoured shields. No invented mounting holes.',
 'CPS_reference':'Training 3-4 / PDF 88 identifies rear NA camshaft-profile-switching solenoids. New envelopes are not gallery plugs.',
 'under_manifold_closures':'Not verified in reviewed factory sources. No additional plugs modeled.'}
(OUT/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2))
# Review studio, excluded from GLB export above.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
# Ground and studio lights.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.37));floor=bpy.context.object;floor.name='REVIEW_STUDIO / excluded from GLB';floor.data.materials.append(material('Studio ground',(.025,.037,.047),.0,.6))
def area(name,pos,power,size):
 bpy.ops.object.light_add(type='AREA',location=V(pos));light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(V((0,.12,0))-light.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-1.5,2,-1),90,2);area('Rear rim',(1.5,1.6,1.7),120,1.8);area('Fill',(1,1,-1.8),65,1.5)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Review orthographic camera';cam.data.type='ORTHO';cam.data.ortho_scale=1.65;scene.camera=cam
views={'assembled':(-1.25,1.1,-1.5),'rear':(.85,.7,1.65),'top':(0,2,.001),'left':(-2,.35,0),'valley':(-.7,1.3,-.9),'rear-exposed':(.55,.45,1.8),'exploded':(-1.1,1.1,-1.5)}
# Non-physical diagnostic collections. They are not included in the physical GLB above.
data=json.loads((Path(__file__).parent/'diagnostic-data.json').read_text())
(OUT/'diagnostic-data.json').write_text(json.dumps(data,indent=2))
diag=bpy.data.collections.new('DIAGNOSTIC_OVERLAYS / NON PHYSICAL');scene.collection.children.link(diag)
def move_collection(ob,col):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob)
annotation_objects=[]
for spec in data['overlays']:
 g=bpy.data.objects.new('overlay__'+spec['id'],None);diag.objects.link(g);g['role']='diagnostic_overlay';g['evidence_status']=spec['status'];g['physical_feature']=False;g['description']=spec['detail'];annotation_objects.append(g)
 # Temporary key allows reuse of mesh helper without making it a physical assembly.
 key='annotation_'+spec['id'];ASSEMBLIES[key]=g
 for j,line in enumerate(spec['paths']):
  ob=tube(spec['label']+' / '+str(j),line['points'],.0016,key,'amber' if spec['kind']!='interface' else 'seal',8);ob['role']='diagnostic_overlay';ob['physical_feature']=False;move_collection(ob,diag);annotation_objects.append(ob)
 del ASSEMBLIES[key]
access_col=bpy.data.collections.new('ACCESS_CAMERA_PROPOSALS / CLEARANCES UNVERIFIED');scene.collection.children.link(access_col)
for spec in data['camera_approaches']:
 ob=bpy.data.objects.new('proposal__'+spec['id'],None);access_col.objects.link(ob);ob.location=V(spec['position']);ob.empty_display_type='CONE';ob.empty_display_size=.06;ob['role']='camera_approach_proposal';ob['clearance_verified']=False;ob['target_gltf']=spec['target'];ob['description']=spec['detail']
for ob in annotation_objects:
 if ob.type=='MESH':clean_mesh(ob)
# Separate overlay GLB can be imported optionally with the physical asset at the same datum.
bpy.ops.object.select_all(action='DESELECT')
for ob in annotation_objects:ob.select_set(True)
bpy.context.view_layer.objects.active=annotation_objects[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/'aj133-phase2b-overlays.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_animations=False)
for ob in annotation_objects:ob.hide_render=True
# Diagnostic collections can be toggled in Blender's Outliner. Default render is physical-only.

# Save assembled editable source, with camera and studio kept outside engine root.
cam.location=V(views['assembled']);cam.rotation_euler=(V((0,.10,.08))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'aj133-na-phase2b-r01.blend'))
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
print('AJ133 Phase 2B reconstruction exported:',OUT)
