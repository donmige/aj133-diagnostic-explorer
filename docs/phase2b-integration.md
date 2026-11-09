# Phase 2B integration record

## Scope and implementation

The approved Phase 2B r01 physical GLB is served unchanged from `public/models/aj133-phase2b.glb`. No further geometry reconstruction or production promotion is part of this change.

1. Preserve all twelve diagnostic IDs and the existing `aj133-case-v1` record; make model choice independent from case state.
2. Default to the GLB and retain the procedural Phase 1 model, including automatic fallback on asset failure.
3. Map nineteen GLB assembly groups to the existing nine assembly controls. Independent overrides operate per component; group changes clear that group's overrides. Materials are cloned so transparency never leaks across components or model reloads.
4. Read GLB anchor world transforms after applying per-group explosion vectors. Markers inherit assembly visibility; schematic markers use corresponding procedural displacements.
5. Attach evidence regions and migration annotations to the GLB groups named in the approved diagnostic JSON. Use clearly hypothetical lines, without adding plugs or passages.
6. Scale the estimated model coordinates uniformly by 3.5 for the existing viewer. Proposed camera positions and targets use the same transform. Coordinates remain +Y up, vehicle left -X and rear +Z.
7. Retain the responsive interface and all case features. Cap device pixel ratio at 1.5; keep cached geometry and dispose only per-instance cloned materials on unmount.

## Evidence limits

Rear-head ball plugs and under-manifold closures have no verified position/function map. The upper rear-block threaded-plug concern is documented by SSM51477, but the regional outline is not an exact centre or bank identification. PDI observations do not establish probabilities for the supplied case. Round rear-head exterior projections identify estimated NA CPS solenoid envelopes. All castings, clearances and context boundaries remain unmeasured.

Proposed viewpoint lines are not probe trajectories or proven physical access. Hypothetical oil paths are not fluid simulation or verified casting channels. During explosion, component-local annotations do not describe continuous connections between separated components.

## Verification

- Next.js optimized build and TypeScript validation.
- Existing functional/regression coverage for diagnostic selection, case persistence/export, navigation, grouped controls and mobile layout.
- Browser checks for model selection, marker displacement, independent states, grouped overrides, hypotheses, all six proposed cameras, preserved case records and failed-asset fallback.
- Asset SHA-256 pinned to the approved review GLB; every component, diagnostic parent and overlay parent checked against the binary asset metadata.
- Browser tests run against the optimized local build; software WebGL is used in the cloud. This is not a guarantee of frame rate on every device.

The dedicated AJ133 Vercel project is `prj_eM8pA3PXIPuUU2xW23XdVu9sSiYL` under the Donmige team. It is separate from Donmige's Automotive. The existing unmerged prototype PR is the review destination; no main-branch update or production deployment is authorized.
