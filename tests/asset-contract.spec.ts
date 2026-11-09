import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import components from '../lib/phase2b-components.json';
import diagnosticData from '../lib/phase2b-diagnostics.json';
import {points} from '../lib/data';
test('approved asset and integration metadata agree for every component, anchor and overlay',()=>{
 const bytes=readFileSync('public/models/aj133-phase2b.glb');
 expect(createHash('sha256').update(bytes).digest('hex')).toBe('bb49a98e2ac16dc91a87b3c9b3934956135aa8f9375b9792c4ddd192e78b872d');
 const glb=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
 type Node={name:string;children?:number[];extras?:{assembly_key?:string;diagnostic_id?:string;explode_vector_gltf?:number[]}};
 const nodes:Node[]=glb.nodes;const groups=nodes.filter(n=>n.extras?.assembly_key);
 expect(groups).toHaveLength(19);expect(components).toHaveLength(groups.length);
 for(const c of components){const node=groups.find(n=>n.name===c.name)!;expect(node.extras?.assembly_key).toBe(c.assembly);expect(node.extras?.explode_vector_gltf).toEqual(c.explode)}
 const parents=new Map<number,Node>();nodes.forEach(n=>n.children?.forEach(i=>parents.set(i,n)));
 for(const point of points){const index=nodes.findIndex(n=>n.extras?.diagnostic_id===point.id);expect(index).toBeGreaterThanOrEqual(0);expect(parents.get(index)?.extras?.assembly_key).toBeTruthy()}
 for(const o of diagnosticData.overlays)for(const path of o.paths)expect(groups.some(g=>g.name===path.parent)).toBe(true);
 expect(diagnosticData.camera_approaches).toHaveLength(6);
});
