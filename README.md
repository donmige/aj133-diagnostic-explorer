# AJ133 Diagnostic Explorer

Diagnostic visualization for the **2012 Range Rover Sport L320 5.0L naturally aspirated AJ133 V8**. No authentication, database, automatic diagnosis or invented probabilities.

## Run locally

Requires Node.js 20.9+ and npm.

```sh
npm ci
npm run dev
```

Open http://localhost:3000 on the machine running the server. For an optimized local build, run `npm run build` then `npm start`. The server binds to 0.0.0.0; a remote Codex environment's localhost is not your Windows localhost. Use the separately supplied Vercel preview for remote viewing.

## Models and controls

**Phase 2B is the default:** a lightweight modular, reference-based exterior reconstruction. **Phase 1 schematic** remains available in the Viewer model selector and is activated automatically if the GLB fails to load. Model changes preserve the selected diagnostic location, notes and inspection statuses; component overrides reset to avoid incompatible states.

- Drag to rotate, scroll/pinch to zoom, right-drag/two-finger gestures to pan. Six face presets plus perspective.
- Explode with the slider; markers remain attached to their source assemblies, including in the schematic fallback. Hidden Phase 2B assemblies hide their markers and attached regions.
- Assembly buttons cycle **solid → ghost → hidden → solid**. Expand Individual Phase 2B components for independent head, gasket, cover, manifold, shield and carrier controls. A grouped change clears that group's individual overrides.
- Click a Phase 2B surface or component name to select its assembly. Numbered markers and diagnostic cards select stable diagnostic IDs.
- Oil pathways enable hypothetical migration curves. Individual investigation-region controls include unresolved head/block zones, estimated gasket outlines and supplied lower-seam accumulation.
- Proposed inspection viewpoint selects one of six camera positions. Violet sightlines are proposals, **not confirmed access routes, openings or probe-fit tests**.
- PCV remains conceptual plumbing. Installed mode adds unmeasured context, not a verified installation or clearance model.
- Reset restores the standard perspective, component states and zero explosion. Overlay toggles retain their settings.
- Notes and statuses retain the existing `aj133-case-v1` localStorage schema and all 12 diagnostic IDs. Export case JSON for backup. Data is browser/origin-local; a different preview hostname has separate browser storage. There is no import or cross-device sync.

## Accuracy and evidence

**All detailed contours, positions and dimensions are approximate and unmeasured.** The reconstruction is not CAD, a service procedure or an engineering simulator. Separate LH/RH groups do not establish the true bank-specific casting contours. The round rear-head projections represent estimated naturally aspirated camshaft profile-switching solenoid envelopes, **not ball-style plugs**.

JLR [SSM51477](https://static.nhtsa.gov/odi/tsbs/2013/MC-10072200-0699.pdf) documents a possible upper rear block threaded-plug leak and references SSM49817. Its PDI context and discussion of anti-corrosion oil do not establish a diagnosis or likelihood for this used vehicle. Exact model-space plug centres remain unresolved. The broad regional overlay is not a plug map. Rear-head ball plugs, internal oil connections and under-manifold closures remain unverified; none were added as physical geometry.

Factory training and parts-diagram references, per-region evidence descriptions and source links are retained in `lib/phase2b-diagnostics.json` and `modeling/phase2b/research-and-accuracy.json`. The earlier reconstruction report and source remain in `modeling/phase2b`. Naturally aspirated components are not assumed identical to supercharged parts.

“Component fact” identifies a represented interface or supplied observation, **not a verified leak or measured position**. Pump/sensor markers and PCV lines remain approximate. Migration curves are hypotheses, not simulated flow or actual casting channels. During explosion they are assembly-local annotations and do not imply connections across separated components. Smoke and accumulation do not identify a source.

## Architecture and performance

- `components/EngineScene.tsx`: Canvas, camera, Phase 1 fallback and shared controls.
- `components/Phase2B.tsx`: cached GLTF loader, per-instance materials, modular visibility/ghost/explosion adapter, scene selection and assembly-local overlays.
- `components/DiagnosticMarker.tsx`: accessible projected DOM markers using anchor world transforms.
- `lib/data.ts`: stable diagnostic IDs and case history.
- `lib/phase2b-components.json`: 19 component keys, nine UI assemblies and GLB explosion metadata.
- `lib/phase2b-diagnostics.json`: evidence regions, hypothetical migration and proposed cameras.
- `public/models/aj133-phase2b.glb`: approved Phase 2B physical geometry, unchanged from review (691,384 bytes; 31,484 triangles; 40 mesh primitives; no textures).

The model is loaded once through Drei's cache. Instance materials are cloned for independent opacity and released on unmount. Device pixel ratio is capped at 1.5. No new runtime dependencies, database or analytics were added. WebGL is required; transparent surfaces may overlap imperfectly. Mobile has a stacked layout. Software-rendered browser tests establish functionality, not hardware frame-rate guarantees.

## Tests

```sh
npm run build
npm test
```

Playwright uses `/usr/bin/chromium` in the supplied cloud environment. Elsewhere, install Chromium with `npx playwright install chromium` and adapt `executablePath` in `playwright.config.ts`.

The original suite checks navigation, rendering, status/notes persistence and export, camera/explosion/group controls and mobile overflow. Phase 2B tests additionally check the default/fallback selector, actual marker world displacement, independent components and group overrides, hypothesis toggles, six proposed camera choices, failed-asset fallback and case preservation. The asset-contract test checks every diagnostic anchor has an assembly parent and all overlay/component names resolve.

## Publishing

Changes are reviewed through an unmerged feature pull request and a **preview-only** deployment in the dedicated `aj133-diagnostic-explorer` Vercel project. No Donmige's Automotive project is part of this application. Production promotion and merging require separate approval.
