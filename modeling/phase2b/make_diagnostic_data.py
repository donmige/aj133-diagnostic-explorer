"""Non-physical regions and camera proposals. No actual plug, gallery or clearance geometry."""
import json,math
from pathlib import Path
OUT=Path(__file__).parent
ssm='https://static.nhtsa.gov/odi/tsbs/2013/MC-10072200-0699.pdf'
head='https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43096/brand/land-rover/'
block='https://parts.jaguarlandroverclassic.com/parts/index/part/id/23.52945.53046.43093/brand/land-rover/'
def path(points,parent):return {'points':points,'parent':parent}
def rectangle(side,y0,y1,x0,x1,z):return [[side*x0,y0,z],[side*x1,y0,z],[side*x1,y1,z],[side*x0,y1,z],[side*x0,y0,z]]
def gasket(side):
 n=(side/math.sqrt(2),1/math.sqrt(2));u=(side/math.sqrt(2),-1/math.sqrt(2))
 return [[side*.205+w*u[0]+.002*n[0],.205+w*u[1]+.002*n[1],z] for w,z in [(-.129,-.30),(.129,-.30),(.129,.29),(-.129,.29),(-.129,-.30)]]
overlays=[]
for side,bank in [(-1,'LH'),(1,'RH')]:
 overlays.append({'id':'head-'+bank.lower(),'label':bank+' rear head / plug investigation','kind':'region','status':'UNRESOLVED','color':'#ffbd68','defaultVisible':True,'paths':[path(rectangle(side,.23,.40,.18,.36,.322),'Head_'+bank)],'detail':'Region only. Exact ball-style closure positions and oil-passage functions were not established in the reviewed factory sources. Outline is not a plug or service-access opening.','sources':[head]})
overlays.append({'id':'block-gallery','label':'Rear block gallery-plug investigation','kind':'region','status':'DOCUMENTED_SOURCE_APPROXIMATE_REGION','color':'#ffbd68','defaultVisible':True,'paths':[path([[-.30,.07,.327],[.30,.07,.327],[.30,.20,.327],[-.30,.20,.327],[-.30,.07,.327]],'RearFace')],'detail':'SSM51477 identifies a threaded plug at an upper rear block corner and references SSM49817. The broad band bounds an investigation area; it does not identify a plug centre or a bank. Exact side/centre/diameter on this reconstruction remain unverified. No physical plug is modeled.','sources':[ssm,block]})
for side,bank in [(-1,'LH'),(1,'RH')]:
 overlays.append({'id':'gasket-'+bank.lower(),'label':bank+' external head-gasket perimeter','kind':'interface','status':'VERIFIED_INTERFACE_ESTIMATED_OUTLINE','color':'#6edce1','defaultVisible':False,'paths':[path(gasket(side),'HeadGasket_'+bank)],'detail':'The head/block sealing interface is verified. This external outline, thickness and position are estimated; no oil or coolant passages are represented.','sources':[head]})
for side,bank in [(-1,'LH'),(1,'RH')]:
 overlays.append({'id':'oil-'+bank.lower(),'label':'Hypothetical oil migration / '+bank+' exhaust','kind':'hypothesis','status':'HYPOTHETICAL_NOT_CONFIRMED_FLOW','color':'#f79b47','defaultVisible':False,'paths':[path([[side*.26,.34,.34],[side*.34,.23,.34],[side*.405,.19,.27],[side*.47,.13,.19],[side*.47,.09,.07]],'Block')],'detail':'Illustrative possible external migration toward a hot exhaust surface. No leak source, drain, gallery connection or probability is established. Not simulated oil flow.','sources':[]})
overlays.append({'id':'rear-runoff','label':'Hypothetical migration toward lower seam','kind':'hypothesis','status':'DOCUMENTED_PATTERN_HYPOTHETICAL_CURVE','color':'#f79b47','defaultVisible':False,'paths':[path([[0,.17,.342],[.11,.06,.347],[.13,-.07,.35],[.08,-.22,.357],[0,-.34,.36]],'RearFace')],'detail':'SSM51477 describes oil from the upper rear block plug collecting around the lower bellhousing. This curve is hypothetical; it does not verify a casting channel or identify the source in this case. The bulletin concerns PDI and also discusses anti-corrosion oil.','sources':[ssm]})
overlays.append({'id':'lower-seam','label':'Lower bellhousing seam / accumulation region','kind':'observation','status':'SUPPLIED_CASE_OBSERVATION_POSITION_ESTIMATED','color':'#ffd58b','defaultVisible':True,'paths':[path([[-.09,-.322,.36],[-.06,-.35,.36],[.06,-.35,.36],[.09,-.322,.36]],'RearFace')],'detail':'The supplied case reports accumulation at the lower engine/transmission seam. Its placement is estimated. Accumulation does not prove a rear main seal leak.','sources':[]})
for side,bank in [(-1,'LH'),(1,'RH')]:
 overlays.append({'id':'block-side-'+bank.lower(),'label':bank+' hidden exhaust-side block region','kind':'region','status':'UNRESOLVED_NO_VERIFIED_CLOSURES','color':'#d9a1ff','defaultVisible':False,'paths':[path([[side*.323,-.04,-.21],[side*.323,.105,-.21],[side*.323,.105,.24],[side*.323,-.04,.24],[side*.323,-.04,-.21]],'Block')],'detail':'Investigation area behind the manifold. Reviewed sources do not establish additional pressurized-oil closures beneath the NA manifolds. Absence of confirmation is not proof of absence. No plugs or passages have been added.','sources':[block,head]})
access=[
 {'id':'above-rear','label':'Above / behind heads','position':[0,1.12,1.03],'target':[0,.30,.30]},
 {'id':'under-rear','label':'Underneath / rear block','position':[.05,-.93,1.03],'target':[0,-.04,.32]},
 {'id':'left-wheel','label':'LH wheel-well direction','position':[-1.15,.13,.18],'target':[-.33,.18,.12]},
 {'id':'right-wheel','label':'RH wheel-well direction','position':[1.15,.13,.18],'target':[.33,.18,.12]},
 {'id':'joint-lh','label':'LH head/block joint','position':[-.85,.62,.75],'target':[-.27,.22,.27]},
 {'id':'joint-rh','label':'RH head/block joint','position':[.85,.62,.75],'target':[.27,.22,.27]},
]
for c in access:c.update({'status':'PROPOSED_CAMERA_APPROACH_NOT_VERIFIED_CLEARANCE','detail':'Viewpoint proposal only. No wheel-well opening, probe fit, collision-free trajectory, required removal or installed vehicle clearance is established.'})
data={'version':'phase2b-r01','coordinates':'+X vehicle right, +Y up, +Z rear; estimated metres','overlay_disclaimer':'Regions and paths are non-physical annotations. Amber = unresolved/source region, cyan = sealing interface, orange dashed = hypothetical migration, violet = proposed camera approaches.','overlays':overlays,'camera_approaches':access,'firewall_context':{'position_z':.78,'status':'ARBITRARY_CONTEXT_BOUNDARY_NOT_MEASURED','detail':'Representative firewall plane only; its location is arbitrary and cannot establish clearance.'}}
(OUT/'diagnostic-data.json').write_text(json.dumps(data,indent=2))
print('Wrote',len(overlays),'selectable overlays and',len(access),'proposed camera approaches')
