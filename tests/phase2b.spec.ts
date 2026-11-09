import {test,expect} from '@playwright/test';
const headMarker='Rear cylinder-head ball-style plugs';
test('Phase 2B default, attached markers, independent components, overlays and fallback retain case',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>localStorage.setItem('aj133-case-v1',JSON.stringify({notes:'Previously repaired upper leaks',statuses:{'head-plugs':'Reference required',gallery:'Inspect next'}})));
 await page.goto('/');await expect(page.getByLabel('Viewer model')).toHaveValue('phase2b');
 const marker=page.getByRole('button',{name:headMarker,exact:true});await expect(marker).toBeVisible();
 await marker.click();await expect(page.getByLabel('Inspection status')).toHaveValue('Reference required');
 const world=async()=>((await marker.getAttribute('data-world'))||'').split(',').map(Number);
 const before=await world();await page.getByLabel('Exploded view').fill('1');
 await expect.poll(async()=>(await world())[0]-before[0]).toBeCloseTo(.13*3.5,3);
 expect((await world())[1]-before[1]).toBeCloseTo(.11*3.5,3);
 await page.getByText('Individual Phase 2B components',{exact:true}).click();
 await page.getByRole('button',{name:'Head_RH: solid',exact:true}).click();
 await page.getByRole('button',{name:'Head_RH: ghost',exact:true}).click();await expect(marker).toBeHidden();
 await expect(page.getByRole('button',{name:'Head_LH: solid',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Cylinder heads: solid',exact:true}).click();await expect(marker).toBeVisible();await expect(page.getByRole('button',{name:'Head_RH: ghost',exact:true})).toBeVisible();
 await page.getByText('Investigation regions & interfaces',{exact:true}).click();
 await page.getByLabel('Hypothetical oil migration / LH exhaust',{exact:true}).check();
 await expect(page.getByLabel('Hypothetical oil migration / LH exhaust',{exact:true})).toBeChecked();
 await page.getByLabel('Proposed inspection viewpoint').selectOption('2');await expect(page.getByRole('button',{name:'Proposed viewpoints',exact:true})).toHaveAttribute('aria-pressed','true');
 await expect(page.locator('.phase2b-controls')).toContainText('not');
 await page.getByLabel('Viewer model').selectOption('schematic');await expect(marker).toBeVisible();await expect(page.getByLabel('Inspection status')).toHaveValue('Reference required');
 await page.getByLabel('Viewer model').selectOption('phase2b');await expect(marker).toBeVisible();
 await page.getByRole('button',{name:'Diagnostic Notes',exact:true}).click();await expect(page.getByLabel('Case observations & next inspection steps')).toHaveValue('Previously repaired upper leaks');
 await page.getByRole('button',{name:'Reset viewer',exact:true}).click();await expect(page.locator('output')).toHaveText('0%');
 expect(errors).toEqual([]);
});
test('asset failure automatically uses schematic fallback without losing notes',async({page})=>{
 await page.route('**/models/aj133-phase2b.glb',route=>route.abort());
 await page.goto('/');await expect(page.getByRole('alert').filter({hasText:'Phase 2B asset'})).toContainText('schematic fallback');await expect(page.getByLabel('Viewer model')).toHaveValue('schematic');await expect(page.getByRole('button',{name:headMarker,exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Diagnostic Notes',exact:true}).click();await page.getByLabel('Case observations & next inspection steps').fill('Fallback still usable');await expect(page.getByText('Saved in this browser',{exact:true})).toBeVisible();
});
test('mobile Phase 2B controls and all six proposed cameras',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');await expect(page.getByRole('button',{name:headMarker,exact:true})).toBeVisible();
 for(let i=0;i<6;i++){await page.getByLabel('Proposed inspection viewpoint').selectOption(String(i));await expect(page.getByRole('button',{name:'Proposed viewpoints',exact:true})).toHaveAttribute('aria-pressed','true')}
 await page.getByLabel('Viewer model').selectOption('schematic');await page.getByLabel('Viewer model').selectOption('phase2b');await expect(page.getByRole('button',{name:headMarker,exact:true})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
