# AJ133 Diagnostic Explorer

A local diagnostic visualization prototype for the **2012 Range Rover Sport 5.0L naturally aspirated AJ133 V8**. No deployment, authentication, database or automatic diagnosis.

## Run

Requires Node.js 20.9+ and npm.

```sh
npm ci
npm run dev
```

Open http://localhost:3000. For a production build locally: `npm run build` then `npm start`.

## Use

- Drag to rotate, scroll/pinch to zoom, right-drag/two-finger gestures to pan. Camera presets cover all six faces plus perspective.
- Explode assemblies with the slider. Reset restores camera, assembly states and explosion.
- Assembly buttons cycle **solid → ghost → hidden → solid**.
- Click numbered markers or location cards to read evidence and change inspection status.
- Overlay toggles show illustrative migration, conceptual PCV and an unverified borescope planning curve.
- Installed mode adds schematic chassis/firewall context.
- Notes and location statuses save under `aj133-case-v1` in this browser's localStorage. Use Export case JSON for a portable backup. Clearing browser storage removes the saved case. There is no import or cross-device sync.

## Evidence and limitations

**All geometry, marker coordinates and access curves are schematic, not to scale and not mechanically validated.** No CAD or AJ133 workshop references were provided. No actual oil galleries, casting plugs, fastener positions, drain connections, probe clearances or removal procedures are claimed.

“Component fact” identifies a represented component/interface or a supplied case observation, **not a verified leak or position**. “Suspected” is an unconfirmed hypothesis. “Reference required” marks a location or applicability that needs technical confirmation. The gallery-plug claim is attributed to the supplied brief, not independently documented by this app. Rear head plugs and their oil connections remain unverified.

The oil cooler, pump/sensor markers and PCV plumbing are placeholders. Borescope and runoff curves are illustrative. Installed context cannot establish real access. Explosion separates groups for understanding only: overlays and markers remain at assembled coordinates. Smoke and accumulation do not identify a source; no probabilities or automatic diagnosis are produced.

WebGL is required. Transparent surfaces may overlap imperfectly. The small procedural model favors clarity over fidelity; mobile has a stacked layout. Status and notes are local only. Fonts use Google Fonts with system fallbacks; no case data is sent externally.

## Architecture / later CAD integration

- `lib/data.ts`: stable diagnostic IDs, evidence, inspection text, coordinate anchors, assemblies and camera names.
- `components/EngineScene.tsx`: isolated React Three Fiber Canvas, procedural assembly groups, Drei controls/lines and projected accessible DOM markers. No internal rotating engine parts.
- `components/Explorer.tsx`: workspace navigation, layer states, case state and persistence.
- `app/globals.css`: responsive technical UI.

To integrate an accurate GLB, replace the procedural `Engine` geometry with a `useGLTF` adapter exposing these same assembly keys. Normalize CAD coordinates to **Y up, front −Z, rear +Z, vehicle left −X** and a documented scale. Separate each assembly's mesh group and material so visibility/opacity/explosion apply independently. Replace marker anchors, explosion vectors and route paths with technically reviewed coordinates, record source documents/revisions and update evidence labels only after review. Existing diagnostic IDs preserve notes/statuses. No GLB loader UI or verified CAD is included in v1.

## Tests

```sh
npm test
```

Playwright config uses `/usr/bin/chromium` in the supplied cloud environment. On another system install Chromium with `npx playwright install chromium`, then remove `executablePath` from `playwright.config.ts` or set it to your Chromium path. Tests cover rendering, marker selection, status persistence, notes persistence/export, camera/explosion/visibility controls, overlays and mobile overflow. `npm run build` validates TypeScript and Next.js compilation.
