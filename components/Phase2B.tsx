'use client';
import {Component,Fragment,ReactNode,useEffect,useMemo} from 'react';
import {createPortal} from '@react-three/fiber';
import {useGLTF,Line,RoundedBox} from '@react-three/drei';
import {Mesh,Material,Object3D,Vector3} from 'three';
import {points} from '../lib/data';
import {componentState} from '../lib/model';
import data from '../lib/phase2b-diagnostics.json';
import type {Props} from './EngineScene';
import {Marker} from './DiagnosticMarker';

class AssetBoundary extends Component<{children:ReactNode;onError:()=>void},{failed:boolean}>{
 state={failed:false};static getDerivedStateFromError(){return {failed:true}}
 componentDidCatch(){this.props.onError()}
 render(){return this.state.failed?null:this.props.children}
}
function Model(p:Props){
 const loaded=useGLTF('/models/aj133-phase2b.glb');
 const model=useMemo(()=>{const root=loaded.scene.clone(true);root.traverse(o=>{if(o instanceof Mesh)o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone()});return root},[loaded.scene]);
 const groups=useMemo(()=>{const result:Record<string,Object3D>={};model.traverse(o=>{if(o.userData.assembly_key){result[o.name]=o;o.userData.basePosition=o.position.clone()}});return result},[model]);
 useEffect(()=>()=>{model.traverse(o=>{if(o instanceof Mesh){const materials:Material[]=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>m.dispose())}})},[model]);
 useEffect(()=>{for(const [name,g] of Object.entries(groups)){const state=componentState(name,p.assembly);g.visible=state!=='hidden';g.position.copy(g.userData.basePosition).addScaledVector(new Vector3(...g.userData.explode_vector_gltf),p.explode);g.traverse(o=>{if(o instanceof Mesh){const mats:Material[]=Array.isArray(o.material)?o.material:[o.material];for(const mat of mats){mat.transparent=state==='ghost';mat.opacity=state==='ghost'?.2:1;mat.depthWrite=state!=='ghost';mat.needsUpdate=true}}})}},[groups,p.assembly,p.explode]);
 const anchors=useMemo(()=>Object.fromEntries(points.map(point=>[point.id,model.getObjectByName('anchor__'+point.id)!])),[model]);
 return <group scale={3.5}>
 <primitive object={model} dispose={null} onClick={event=>{event.stopPropagation();let object:Object3D|null=event.object;while(object&&!object.userData.assembly_key)object=object.parent;if(object)p.onComponentSelect(object.name)}}/>
 {p.markers&&points.map((point,i)=><Marker key={point.id} point={point} index={i} selected={p.selected===point.id} onSelect={p.onSelect} anchor={anchors[point.id]}/>)}
 {data.overlays.filter(o=>p.overlays.includes(o.id)||(p.oil&&o.kind==='hypothesis')).flatMap(spec=>spec.paths.map((path,i)=><Fragment key={spec.id+i}>{createPortal(<Line points={path.points as [number,number,number][]} color={spec.color} lineWidth={2} dashed={spec.kind==='hypothesis'} dashSize={.015} gapSize={.01} depthTest={false}/>,groups[path.parent])}</Fragment>))}
 {p.pcv&&<Line points={[[-.3,.45,-.15],[-.2,.6,-.15],[.2,.6,-.15],[.3,.45,-.15]]} color="#68d5e5" lineWidth={3} dashed dashSize={.02} gapSize={.015}/>}
 {p.scope&&data.camera_approaches.map(c=><Line key={c.id} points={[c.position,c.target] as [number,number,number][]} color="#b9a2ff" lineWidth={2} dashed dashSize={.03} gapSize={.02} depthTest={false}/>)}
 {p.installed&&<RoundedBox args={[1.4,1.05,.01]} position={[0,.16,1]} radius={.01}><meshStandardMaterial color="#405560" wireframe transparent opacity={.3}/></RoundedBox>}
 </group>
}
export default function Phase2B(p:Props){return <AssetBoundary onError={p.onModelError}><Model {...p}/></AssetBoundary>}
