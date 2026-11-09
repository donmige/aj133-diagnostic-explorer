'use client';
import {useThree,useFrame} from '@react-three/fiber';
import {useEffect,useRef} from 'react';
import {Object3D,Vector3} from 'three';
import {points} from '../lib/data';
export function Marker({point,index,selected,onSelect,anchor,offset=[0,0,0]}:{point:typeof points[number];index:number;selected:boolean;onSelect:(id:string)=>void;anchor?:Object3D;offset?:[number,number,number]}){
const {gl,camera}=useThree();const ref=useRef<HTMLButtonElement|null>(null);const vector=useRef(new Vector3());
useEffect(()=>{const button=document.createElement('button');button.style.position='absolute';button.style.zIndex='20';button.setAttribute('aria-label',point.name);button.title=point.name;button.textContent=String(index+1).padStart(2,'0');button.onclick=()=>onSelect(point.id);gl.domElement.parentElement!.appendChild(button);ref.current=button;return()=>{button.remove();ref.current=null}},[gl,index,point,onSelect]);
useEffect(()=>{if(ref.current)ref.current.className='marker '+(selected?'selected':'')},[selected,onSelect]);
useFrame(()=>{const button=ref.current;if(!button)return;const v=vector.current;if(anchor){anchor.getWorldPosition(v)}else{v.set(point.position[0]+offset[0],point.position[1]+offset[1],point.position[2]+offset[2]);v.y+=.25}button.dataset.world=v.toArray().join(',');let visible=true;for(let o: Object3D|null=anchor||null;o;o=o.parent)visible=visible&&o.visible;v.project(camera);const width=gl.domElement.clientWidth,height=gl.domElement.clientHeight;button.style.left=((v.x+1)*width/2-12.5)+'px';button.style.top=((-v.y+1)*height/2-12.5)+'px';button.style.display=!visible||v.z>1||v.z< -1?'none':'block'});return null;
}
