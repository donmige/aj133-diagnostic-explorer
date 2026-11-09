AJ133 DIAGNOSTIC EXPLORER — PHASE 2B REVIEW PACKAGE

SEPARATE MODEL STUDY. No production application change, integration, merge or deployment.
Target: 2012 Range Rover Sport L320 5.0 naturally aspirated AJ133 V8.
All reconstructed dimensions and detailed casting contours are estimates, NOT measured CAD.

OPEN THE INTERACTIVE REVIEW ON WINDOWS
1. Extract this complete ZIP.
2. Open review.html in a WebGL-capable browser such as Edge or Chrome.
   Model bytes, fallback model, Three.js and controls are embedded. No CDN or
   remote localhost connection is needed. The file does not upload case data.
3. If your browser blocks local HTML scripts, serve this extracted folder on YOUR
   Windows computer, e.g. PowerShell: py -m http.server 8000 --bind 127.0.0.1
   Then open http://localhost:8000/review.html in your Windows browser.
   This optional server is local to Windows, not the remote Codex environment.
The managed cloud browser blocked file:// navigation by policy. The exact embedded
HTML contents were executed and interaction-tested offline in an isolated browser
document, with zero external HTTP requests. See browser-validation.json.

REVIEW CONTROLS
- Orbit, zoom, pan and six camera presets.
- Independent show/hide and opacity controls for all 19 assembly groups.
- Rear heads only; rear block only; LH/RH transparent manifold inspection presets.
- Exploded slider. Separations are illustrative, NOT removal directions.
- 11 selectable diagnostic overlays with explicit evidence/uncertainty text.
- Six PROPOSED camera viewpoints from above, below, wheel-well directions and joints.
- Optional arbitrary firewall boundary for context only, NOT measured clearance.
- Phase 2 fallback comparison selector. The original app UI is not replaced.

EVIDENCE PRIORITIES
Rear block threaded-plug leakage and lower bellhousing accumulation are described
by manufacturer SSM51477 (NHTSA-hosted PDF), which references SSM49817. The latter's
reproduced text/illustration was inspected, but an original factory-hosted attachment
was not retrieved. No exact model-space plug centre was established and no physical
plug was added. The block overlay is one broad investigation band, not two plugs.
Rear head ball-style plug identities and oil-passage connections remain UNRESOLVED.
Additional under-manifold oil closures on the NA engine are also UNRESOLVED.
Do not infer them from supercharged parts. Unconfirmed features are regions only.
Small rear head cylindrical envelopes represent identified NA CPS solenoids in
training page 3-4, NOT ball plugs. Their locations/shapes remain estimated.
The head bank shells share a conservative generic profile where bank-specific rear
casting photographs are missing. Separate bank groups do not prove true symmetry.
Oil migration curves are HYPOTHETICAL, not simulated or confirmed oil flow.
No probabilities, automatic diagnosis, repair/removal instructions or internal
rotating engine parts are included. No borescope fit or installed clearance is verified.

FILES
aj133-na-phase2b-r01.blend — editable source, separate diagnostic/camera-proposal collections.
aj133-na-phase2b-r01.glb — modular physical exterior and 12 existing diagnostic anchor IDs.
aj133-phase2b-overlays.glb — optional NON-PHYSICAL curve annotations, same coordinate datum.
review.html — self-contained interactive review, including embedded original fallback GLB.
review-bundle.js — auditable bundled Three.js/controls/loader script used by review.html.
diagnostic-data.json — evidence-labelled overlay curves and proposed viewpoints.
accuracy-report.html — per-feature changes, uncertainties, sources and remaining evidence gaps.
evidence-manifest.json and research-and-accuracy.json — machine-readable evidence registers.
validation.json — structural GLB validation. browser-validation.json — interaction checks.
rear-engine-hires.png — 2000 x 1500 rear view, bellhousing digitally hidden.
left-exhaust.png and right-exhaust.png — shields and bellhousing digitally hidden.
rear-heads-isolated.png — heads/gaskets only, with estimated CPS envelopes.
rear-block-isolated.png — block, rear face, carrier and sump only.
left-transparent.png and right-transparent.png — ghosted heads/block, opaque manifolds.
phase2-baseline-same-camera.png — original Phase 2 asset, matched rear camera/scale.
phase2-vs-phase2b.png — matched-camera comparison sheet.
review-*.png — interactive review screenshots, including proposed approaches and overlays.
fallback-phase2/ — unchanged Phase 2 .blend, GLB and evidence manifest.
fallback-sha256.json — baseline hashes checked by validation.
source/ — reconstruction, review, rendering and validation scripts/templates.
THIRD_PARTY_THREE_LICENSE.txt — Three.js MIT licence for the embedded review dependencies.
SHA256SUMS.json — checksums for package files (excluding the checksum file itself).

BLENDER
Open the .blend, select AJ133_NA_PHASE2B_R01 in the Outliner and use Frame Selected.
Physical components are separately named. Diagnostic curves and proposed cameras
are separate NON-PHYSICAL collections. Their placement cannot establish real access.
The review studio/cameras are excluded from the physical GLB. No studio floor or
light geometry is part of the engine model. Source file is saved in assembled state.
Metres, +X vehicle right, +Y up, +Z rear in glTF. Scale is estimated, not measured.
Per-group extras.assembly_key retains the existing UI mapping. extras.explode_vector_gltf
is an illustrative offset. Clone shared GLTF materials before changing opacity.
Anchor empties retain IDs for a future adapter; no application adapter is installed.

REPRODUCE IN A DEVELOPMENT WORKSPACE
Requires Blender 4.3+, Python 3. Building the HTML additionally needs esbuild and
three installed in a resolvable node_modules directory. No runtime dependencies
are needed after review.html is built. The supplied browser harness targets the
Linux Codex workspace and its Chromium; adapt paths for another machine.

python source/make_diagnostic_data.py
blender -b -t 4 -P source/reconstruct.py -- --out /your/output
python source/write_report.py --out /your/output
python source/validate_glb.py /your/output/aj133-na-phase2b-r01.glb
blender -b /your/output/aj133-na-phase2b-r01.blend -t 4 -P source/render_review.py -- --out /your/output
python source/build_review.py --out /your/output --esbuild /path/to/esbuild

Keep fallback-phase2/ and fallback-sha256.json in the chosen output directory.
Do not delete or overwrite the existing Phase 2 model when rebuilding Phase 2B.
Structural/browser validation is NOT mechanical, fitment or service-access validation.
