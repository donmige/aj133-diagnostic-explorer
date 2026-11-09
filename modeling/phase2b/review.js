import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
const data=window.REVIEW_DATA;
const viewport=document.querySelector('#viewport'),labelLayer=document.querySelector('#labels');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor('#101a22');viewport.prepend(renderer.domElement);
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xcde7ff,0x3b4145,2.4));
for(const [pos,intensity] of [[[1,2,2],3.2],[[-1,1,-2],2.5]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...pos);scene.add(light)}
const camera=new THREE.PerspectiveCamera(38,1,.01,20);const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,.12,.08);controls.minDistance=.55;controls.maxDistance=5;controls.enableDamping=true;
const grid=new THREE.GridHelper(3,30,0x334956,0x20343f);grid.position.y=-.37;scene.add(grid);
const decoder=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)).buffer;
const loader=new GLTFLoader();
const sourceMeta={};const meshToGroup=new Map();const allGroups={};const overlayEntries=[];const overlayLabels=[];
let current='phase2b',selected=null,accessEnabled=false,explosion=0;
const byId=id=>document.getElementById(id);
const appState={};const clones=[];
function setPose(position,target=[0,.12,.08]){camera.position.set(...position);controls.target.set(...target);controls.update()}
const presets={Rear:[[.6,.46,1.55],[0,.12,.28]],Front:[[-.7,.65,-1.5],[0,.12,0]],Left:[[-1.7,.35,0],[0,.12,.05]],Right:[[1.7,.35,0],[0,.12,.05]],Top:[[0,1.8,.001],[0,.12,.05]],Bottom:[[0,-1.6,.4],[0,-.05,.1]]};
function describe(title,detail,status){byId('detail-title').textContent=title;byId('detail-text').textContent=detail;byId('detail-status').textContent=status}
function selectOverlay(spec){selected=spec.id;describe(spec.label,spec.detail,spec.status);for(const e of overlayEntries)for(const line of e.lines)line.material.color.set(e.spec.id===selected?'#ffffff':e.spec.color);document.querySelectorAll('.overlay-row').forEach(el=>el.classList.toggle('selected',el.dataset.id===selected))}
function setGroupState(key,visible=true,opacity=1){
 const group=allGroups.phase2b[key];if(!group)return;
 appState[key]={visible,opacity};group.visible=visible;
 group.traverse(o=>{if(!o.isMesh)return;const mats=Array.isArray(o.material)?o.material:[o.material];for(const mat of mats){mat.opacity=opacity;mat.transparent=opacity<1;mat.depthWrite=opacity>=1;mat.side=opacity<1?THREE.DoubleSide:THREE.FrontSide;mat.needsUpdate=true}});
 const check=document.querySelector(`[data-visibility="${key}"]`),range=document.querySelector(`[data-opacity="${key}"]`);if(check)check.checked=visible;if(range)range.value=opacity;
}
function resetComponents(){for(const key of Object.keys(allGroups.phase2b))setGroupState(key);byId('explode').value=0;setExplosion(0)}
function setExplosion(value){explosion=value;for(const group of Object.values(allGroups.phase2b)){group.position.copy(group.userData.originalPosition).addScaledVector(new THREE.Vector3(...group.userData.explode_vector_gltf),value)}byId('explode-value').textContent=Math.round(value*100)+'%'}
function isolate(keys){resetComponents();for(const key of Object.keys(allGroups.phase2b))setGroupState(key,keys.includes(key));}
function newLine(points,color,dashed=false){const geo=new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p)));const mat=dashed?new THREE.LineDashedMaterial({color,dashSize:.012,gapSize:.009,depthTest:false,transparent:true,opacity:.95}):new THREE.LineBasicMaterial({color,depthTest:false,transparent:true,opacity:.95});const line=new THREE.Line(geo,mat);if(dashed)line.computeLineDistances();line.renderOrder=10;return line}
async function init(){
 const [refined,fallback]=await Promise.all([loader.parseAsync(decoder(window.MODEL_BYTES),''),loader.parseAsync(decoder(window.MODEL_FALLBACK),'')]);
 sourceMeta.phase2b=refined.scene;sourceMeta.phase2=fallback.scene;
 for(const [which,model] of Object.entries(sourceMeta)){
  allGroups[which]={};model.traverse(o=>{
   if(o.userData.assembly_key&&o.userData.explode_vector_gltf){allGroups[which][o.name]=o;o.userData.originalPosition=o.position.clone()}
   if(o.isMesh){o.castShadow=false;o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();clones.push(o.material)}
  });scene.add(model);model.visible=which===current;
  model.traverse(o=>{if(o.isMesh){let p=o.parent;while(p&&!p.userData.assembly_key)p=p.parent;if(p)meshToGroup.set(o,p)}})
 }
 for(const key of Object.keys(allGroups.phase2b)){
  const g=allGroups.phase2b[key];const row=document.createElement('div');row.className='component-row';
  const check=document.createElement('input');check.type='checkbox';check.checked=true;check.dataset.visibility=key;check.setAttribute('aria-label','Show '+key.replaceAll('_',' '));check.onchange=()=>setGroupState(key,check.checked,Number(range.value));
  const text=document.createElement('button');text.className='component-name';text.textContent=key.replaceAll('_',' ');text.onclick=()=>describe(text.textContent,'Reference-based exterior envelope. Dimensions and detailed contours are estimated. This component view does not establish a leak or a service clearance.','APPROXIMATE_GEOMETRY');
  const range=document.createElement('input');range.type='range';range.min='.12';range.max='1';range.step='.01';range.value='1';range.dataset.opacity=key;range.setAttribute('aria-label','Opacity '+key.replaceAll('_',' '));range.oninput=()=>setGroupState(key,check.checked,Number(range.value));
  row.append(check,text,range);byId('components').append(row);appState[key]={visible:true,opacity:1};
 }
 for(const spec of data.overlays){
  const row=document.createElement('div');row.className='overlay-row';row.dataset.id=spec.id;
  const check=document.createElement('input');check.type='checkbox';check.checked=spec.defaultVisible;check.setAttribute('aria-label',spec.label);
  const button=document.createElement('button');button.textContent=spec.label;button.onclick=()=>selectOverlay(spec);row.append(check,button);byId('overlays').append(row);
  const entry={spec,lines:[],check,material:null};
  for(const path of spec.paths){
   const line=newLine(path.points,spec.color,spec.kind==='hypothesis');line.visible=check.checked;line.userData.overlayId=spec.id;allGroups.phase2b[path.parent].add(line);entry.lines.push(line);entry.material=line.material;
   const centre=path.points.reduce((a,p)=>a.add(new THREE.Vector3(...p)),new THREE.Vector3()).multiplyScalar(1/path.points.length);
   const anchor=new THREE.Object3D();anchor.position.copy(centre);allGroups.phase2b[path.parent].add(anchor);
   const label=document.createElement('button');label.className='scene-label';label.textContent=spec.id.startsWith('head-')?spec.id.toUpperCase():spec.id==='block-gallery'?'BLOCK REGION':spec.id==='lower-seam'?'LOWER SEAM':spec.id.toUpperCase();label.title=spec.label;label.setAttribute('aria-label','Select '+spec.label);label.onclick=()=>selectOverlay(spec);labelLayer.append(label);overlayLabels.push({anchor,label,entry});
  }
  check.onchange=()=>{for(const line of entry.lines)line.visible=check.checked;selectOverlay(spec)};overlayEntries.push(entry);
 }
 for(const side of [-1,1]){
  const bank=side<0?'LH':'RH',anchor=new THREE.Object3D();anchor.position.set(side*.3195,.214,.382);allGroups.phase2b['Head_'+bank].add(anchor);
  const label=document.createElement('button');label.className='scene-label';label.textContent=bank+' CPS ≈';label.style.borderColor='#75c9d0';label.style.color='#9de8eb';label.title='NA camshaft-profile-switching solenoid envelope; not a gallery plug';label.onclick=()=>describe(bank+' NA CPS solenoid envelope','Identified rear NA component in training page 3-4. Shape and mounting centre are estimated. This round projection is NOT a ball-style gallery plug.','IDENTIFIED_COMPONENT_ESTIMATED_POSITION');labelLayer.append(label);overlayLabels.push({anchor,label,entry:{check:{checked:true}}});
 }
 const accessGroup=new THREE.Group();accessGroup.name='Proposed camera approaches / NOT clearances';scene.add(accessGroup);accessGroup.visible=false;
 for(const c of data.camera_approaches){
  const button=document.createElement('button');button.className='access-pose';button.textContent=c.label;button.onclick=()=>{setPose(c.position,c.target);describe(c.label,c.detail,c.status)};byId('approaches').append(button);
  const line=newLine([c.position,c.target],'#c2a0ff',true);accessGroup.add(line);
  const glyph=new THREE.CameraHelper(new THREE.PerspectiveCamera(40,1,.01,.08));glyph.camera.position.set(...c.position);glyph.camera.lookAt(...c.target);glyph.camera.updateMatrixWorld();glyph.update();accessGroup.add(glyph);
 }
 const firewall=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(1.4,1.05)),new THREE.LineDashedMaterial({color:'#728b99',dashSize:.02,gapSize:.015,transparent:true,opacity:.6}));firewall.position.set(0,.16,data.firewall_context.position_z);firewall.computeLineDistances();firewall.visible=false;scene.add(firewall);
 byId('access-mode').onchange=e=>{accessEnabled=e.target.checked;accessGroup.visible=accessEnabled;byId('access-notice').hidden=!accessEnabled;describe('Proposed camera approaches', 'These are viewpoints and sightline proposals only. Firewall and wheel-well clearances are not measured; no probe fit, opening or removal sequence is established.','CLEARANCES_UNVERIFIED')};
 byId('firewall').onchange=e=>{firewall.visible=e.target.checked;byId('firewall-notice').hidden=!e.target.checked};
 byId('explode').oninput=e=>setExplosion(Number(e.target.value));byId('reset').onclick=()=>{resetComponents();setPose(...presets.Rear);for(const entry of overlayEntries){entry.check.checked=entry.spec.defaultVisible;for(const line of entry.lines)line.visible=entry.check.checked}accessEnabled=false;accessGroup.visible=false;firewall.visible=false;byId('access-mode').checked=false;byId('firewall').checked=false;byId('access-notice').hidden=true;byId('firewall-notice').hidden=true;selectOverlay(data.overlays.find(o=>o.id==='block-gallery'))};
 document.querySelectorAll('[data-pose]').forEach(b=>b.onclick=()=>setPose(...presets[b.dataset.pose]));
 byId('isolate-heads').onclick=()=>{isolate(['Head_LH','Head_RH','HeadGasket_LH','HeadGasket_RH']);setPose([0,.43,1.05],[0,.26,.27])};
 byId('isolate-block').onclick=()=>{isolate(['Block','RearFace','RearSealCarrier','Sump_L320']);setPose([.45,.3,1.1],[0,.02,.29])};
 byId('inspect-left').onclick=()=>{resetComponents();setGroupState('Shield_LH',false);setGroupState('Shield_RH',false);setGroupState('Bellhousing_Envelope',false);for(const key of ['Head_LH','Head_RH','Block'])setGroupState(key,true,.22);setPose(...presets.Left)};
 byId('inspect-right').onclick=()=>{byId('inspect-left').click();setPose(...presets.Right)};
 byId('model-version').onchange=e=>{current=e.target.value;for(const [k,m] of Object.entries(sourceMeta))m.visible=k===current;byId('controls-body').inert=current==='phase2';for(const id of ['isolate-heads','isolate-block','inspect-left','inspect-right'])byId(id).disabled=current==='phase2';byId('fallback-note').hidden=current!=='phase2';if(current==='phase2'){accessGroup.visible=false;firewall.visible=false}else{accessGroup.visible=accessEnabled;firewall.visible=byId('firewall').checked}};
 const raycaster=new THREE.Raycaster();raycaster.params.Line.threshold=.009;let pointerDown;
 renderer.domElement.addEventListener('pointerdown',e=>pointerDown=[e.clientX,e.clientY]);renderer.domElement.addEventListener('pointerup',e=>{
  if(!pointerDown||Math.hypot(e.clientX-pointerDown[0],e.clientY-pointerDown[1])>5)return;
  const r=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);
  if(current==='phase2b'){
   const hit=raycaster.intersectObjects(overlayEntries.flatMap(en=>en.lines).filter(l=>{let ob=l;while(ob){if(!ob.visible)return false;ob=ob.parent}return true}),false)[0];if(hit){selectOverlay(data.overlays.find(o=>o.id===hit.object.userData.overlayId));return}
  }
  const hits=raycaster.intersectObject(sourceMeta[current],true).filter(h=>{if(!h.object.isMesh)return false;let ob=h.object;while(ob){if(!ob.visible)return false;ob=ob.parent}return true});if(hits.length){const group=meshToGroup.get(hits[0].object);if(group)describe(group.name.replaceAll('_',' '),'Selected exterior assembly. Shape, fitment and clearances remain approximate; use the evidence report for source limits.','APPROXIMATE_GEOMETRY')}
 });
 setPose(...presets.Rear);selectOverlay(data.overlays.find(o=>o.id==='block-gallery'));
 byId('loading').hidden=true;
 window.review={snapshot(){return {model:current,groups:Object.fromEntries(Object.entries(allGroups.phase2b).map(([k,g])=>[k,{visible:g.visible,opacity:appState[k].opacity,position:g.position.toArray()}])),overlays:Object.fromEntries(overlayEntries.map(en=>[en.spec.id,{checked:en.check.checked,world:en.lines[0].getWorldPosition(new THREE.Vector3()).toArray()}])),explosion,accessEnabled,selected,renderCalls:renderer.info.render.calls}},models:sourceMeta,groups:allGroups};window.reviewReady=true;
}
function resize(){const r=viewport.getBoundingClientRect();renderer.setSize(r.width,r.height);camera.aspect=r.width/r.height;camera.updateProjectionMatrix()}
new ResizeObserver(resize).observe(viewport);
function animate(){requestAnimationFrame(animate);controls.update();scene.updateMatrixWorld(true);renderer.render(scene,camera);
 const r=viewport.getBoundingClientRect();for(const {anchor,label,entry} of overlayLabels){const pos=anchor.getWorldPosition(new THREE.Vector3()).project(camera);let parent=anchor.parent,shown=true;while(parent){shown=shown&&parent.visible;parent=parent.parent}label.hidden=current!=='phase2b'||!entry.check.checked||!shown||pos.z< -1||pos.z>1;label.style.left=((pos.x+1)*r.width/2)+'px';label.style.top=((-pos.y+1)*r.height/2)+'px'}
}
init().catch(error=>{byId('loading').textContent='Review failed to load: '+error.message;window.reviewError=error.message});resize();animate();
