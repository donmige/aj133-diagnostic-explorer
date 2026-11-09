import components from './phase2b-components.json';
export type ModelVersion='phase2b'|'schematic';
export {components};
export function componentState(name:string,assembly:Record<string,string>){const component=components.find(c=>c.name===name);return assembly[name]||assembly[component?.assembly||name]||'solid'}
