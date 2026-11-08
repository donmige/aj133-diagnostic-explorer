'use client';
import {Canvas,useThree,useFrame} from '@react-three/fiber';
import {OrbitControls,Line,ContactShadows,Grid,RoundedBox} from '@react-three/drei';
import {useEffect,useRef} from 'react';
import {Vector3} from 'three';
import {points,View} from '../lib/data';
export type AssemblyState=Record<string,'solid'|'ghost'|'hidden'>;
type Props={reset:number;view:View;explode:number;assembly:AssemblyState;selected:string;onSelect:(id:string)=>void;markers:boolean;oil:boolean;pcv:boolean;scope:boolean;installed:boolean};
const poses:Record<View,[number,number,number]>={Perspective:[-5,3.6,-6],Front:[0,1,-7],Rear:[0,1,7],Top:[0,7,.01],Left:[-7,1,0],Right:[7,1,0],Bottom:[0,-7,.01]};
function Camera({view,reset}:{view:View;reset:number}){const {camera,controls}=useThree();useEffect(()=>{camera.position.set(...poses[view]);camera.lookAt(0,.3,0);camera.updateProjectionMatrix();const orbit=controls as unknown as {target:Vector3;update:()=>void}|null;if(orbit){orbit.target.set(0,.3,0);orbit.update()}},[camera,controls,view,reset]);return null}
function Box({name,at,size,color,rotation=[0,0,0],assembly}:{name:string;at:[number,number,number];size:[number,number,number];color:string;rotation?:[number,number,number];assembly:AssemblyState}){const s={visible:assembly[name]!=='hidden',opacity:assembly[name]==='ghost'?.18:1};return <group visible={s.visible}><RoundedBox position={at} args={size} radius={.07} smoothness={3} rotation={rotation}><meshStandardMaterial color={color} roughness={.56} metalness={.65} transparent opacity={s.opacity}/></RoundedBox></group>}

function Marker({point,index,selected,onSelect}:{point:typeof points[number];index:number;selected:boolean;onSelect:(id:string)=>void}){
const {gl,camera}=useThree();const ref=useRef<HTMLButtonElement|null>(null);const vector=useRef(new Vector3());
useEffect(()=>{const button=document.createElement('button');button.style.position='absolute';button.style.zIndex='20';button.setAttribute('aria-label',point.name);button.title=point.name;button.textContent=String(index+1).padStart(2,'0');button.onclick=()=>onSelect(point.id);gl.domElement.parentElement!.appendChild(button);ref.current=button;return()=>{button.remove();ref.current=null}},[gl,index,point,onSelect]);
useEffect(()=>{if(ref.current)ref.current.className='marker '+(selected?'selected':'')},[selected,onSelect]);
useFrame(()=>{const button=ref.current;if(!button)return;const v=vector.current.set(...point.position);v.y+=.25;v.project(camera);const width=gl.domElement.clientWidth,height=gl.domElement.clientHeight;button.style.left=((v.x+1)*width/2-12.5)+'px';button.style.top=((-v.y+1)*height/2-12.5)+'px';button.style.display=v.z>1||v.z< -1?'none':'block'});return null;
}

function Engine(p:Props){
const state=(name:string)=>({visible:p.assembly[name]!=='hidden',opacity:p.assembly[name]==='ghost'?.18:1});
const e=p.explode;
return <group position={[0,.25,0]}>
<Box assembly={p.assembly} name="Block" at={[0,0,0]} size={[1.9,1.25,2.6]} color="#52636b"/>
{[-1,1].map(side=><group key={side}>
<Box assembly={p.assembly} name="Cylinder heads" at={[side*(.85+e*.45),.78+e*.4,0]} size={[.85,.6,2.65]} rotation={[0,0,-side*.28]} color="#89979b"/>
<Box assembly={p.assembly} name="Valve covers" at={[side*(1.03+e*.7),1.2+e*.9,0]} size={[.78,.32,2.6]} rotation={[0,0,-side*.28]} color="#293a41"/>
{Array.from({length:6},(_,i)=><Box assembly={p.assembly} key={i} name="Valve covers" at={[side*(1.03+e*.7),1.38+e*.9,-1.02+i*.4]} size={[.72,.055,.055]} color="#607379"/>)}
{Array.from({length:4},(_,i)=><mesh key={i} visible={state('Exhaust & shields').visible} position={[side*(1.35+e*.6),.1,-.95+i*.62]} rotation={[0,0,side*1.1]}><torusGeometry args={[.3,.115,10,20,Math.PI]}/><meshStandardMaterial color="#8f7461" metalness={.7} roughness={.7} transparent opacity={state('Exhaust & shields').opacity}/></mesh>)}
<Box assembly={p.assembly} name="Exhaust & shields" at={[side*(1.58+e*.6),.05,0]} size={[.18,.65,2.5]} color="#6e7775"/>
<mesh visible={state('Valve covers').visible} position={[side*(1.04+e*.7),1.52+e*.9,-.65]}><cylinderGeometry args={[.13,.13,.22,20]}/><meshStandardMaterial color="#9aa5a4" transparent opacity={state('Valve covers').opacity}/></mesh>
</group>)}
<Box assembly={p.assembly} name="Intake manifold" at={[0,1.05+e*1.5,-.1]} size={[.8,.55,2.15]} color="#34464c"/>
{Array.from({length:7},(_,i)=><Box assembly={p.assembly} key={i} name="Intake manifold" at={[0,1.34+e*1.5,-.98+i*.29]} size={[.84,.09,.12]} color="#65777c"/>)}
<Box assembly={p.assembly} name="Oil cooler" at={[0,.55+e*.3,-1.48-e*.5]} size={[.75,.5,.38]} color="#a0a8a6"/>
<Box assembly={p.assembly} name="Rear face" at={[0,0,1.37+e*.5]} size={[1.9,1.3,.16]} color="#748386"/>
<mesh visible={state('Bellhousing').visible} position={[0,-.18,1.95+e*1.2]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[1.05,.72,1.0,12]}/><meshStandardMaterial color="#5c6b70" metalness={.65} roughness={.6} transparent opacity={state('Bellhousing').opacity}/></mesh>
<Box assembly={p.assembly} name="Oil pan" at={[0,-.88-e*.8,0]} size={[1.6,.5,2.5]} color="#323f44"/>
<mesh position={[0,-.05,-1.5]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.38,.38,.25,24]}/><meshStandardMaterial color="#29383c" metalness={.8} roughness={.4}/></mesh>
{p.markers&&points.map((point,i)=><Marker key={point.id} point={point} index={i} selected={p.selected===point.id} onSelect={p.onSelect}/>)}
{p.oil&&<><Line points={[[-1.1,1.25,-.3],[-1.32,.6,-.2],[-1.65,.15,.2],[-1.3,-.4,.9],[0,-.96,1.95]]} color="#ffb55c" lineWidth={3} dashed dashSize={.13} gapSize={.1}/><Line points={[[0,.95,.3],[.3,.4,1.1],[.8,-.1,1.5],[0,-.96,1.95]]} color="#ffb55c" lineWidth={3} dashed dashSize={.13} gapSize={.1}/></>}
{p.pcv&&<Line points={[[-1.05,1.55,-.65],[-.65,1.85,-.6],[0,1.9,-.4],[.65,1.85,-.6],[1.05,1.55,-.65]]} color="#68d5e5" lineWidth={4} dashed dashSize={.18} gapSize={.12}/>}
{p.scope&&<Line points={[[2.5,2.2,2.5],[1.8,1.9,1.7],[.8,1.65,1.25],[0,.95,.35]]} color="#b9a2ff" lineWidth={4} dashed dashSize={.1} gapSize={.12}/>}
{p.installed&&<group><RoundedBox args={[5,.12,5.8]} position={[0,-1.65,0]} radius={.05}><meshStandardMaterial color="#30434b" wireframe/></RoundedBox><RoundedBox args={[4.9,2.8,.15]} position={[0,.2,3.3]} radius={.04}><meshStandardMaterial color="#405560" transparent opacity={.2}/></RoundedBox>{[-2.4,2.4].map(x=><RoundedBox key={x} args={[.2,1,5.8]} position={[x,-.6,0]} radius={.03}><meshStandardMaterial color="#405560" transparent opacity={.3}/></RoundedBox>)}</group>}
</group>}
export default function EngineScene(props:Props){return <Canvas shadows camera={{position:poses.Perspective,fov:40}} gl={{antialias:true,preserveDrawingBuffer:true}}><color attach="background" args={['#101a20']}/><fog attach="fog" args={['#101a20',12,25]}/><ambientLight intensity={1.2}/><directionalLight position={[-4,8,-4]} intensity={3}/><directionalLight position={[5,3,4]} intensity={2} color="#a3d9e2"/><Camera view={props.view} reset={props.reset}/><Engine {...props}/><Grid position={[0,-1.55,0]} args={[14,14]} cellSize={.5} cellThickness={.5} cellColor="#24353c" sectionSize={2} sectionColor="#34474d" fadeDistance={16}/><ContactShadows position={[0,-1.5,0]} opacity={.4} scale={10} blur={2.5} far={5}/><OrbitControls makeDefault target={new Vector3(0,.3,0)} minDistance={3} maxDistance={13}/></Canvas>}
