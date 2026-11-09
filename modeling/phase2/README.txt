AJ133 NA exterior reconstruction — Phase 2, revision 01

SEPARATE REVIEW MODEL. Not integrated into the application or deployed.
Target: 2012 Range Rover Sport L320 5.0 naturally aspirated AJ133 V8.
Exact VIN, engine serial, cover/carrier revisions and gearbox are unconfirmed.
All dimensions and clearances are estimated. This is NOT measured CAD.

CONTENTS
aj133-na-exterior-r01.blend — editable Blender source with review studio.
aj133-na-exterior-r01.glb — lightweight modular glTF export, no studio objects.
evidence-manifest.json — per-assembly sources, evidence limits and anchor identities.
validation.json — machine-readable structural checks (not mechanical validation).
reconstruct.py — deterministic Blender 4.3+ build/export/render script.
validate_glb.py — Python standard-library structural validation.
browser-validation.json — isolated Three.js load/raycast/opacity/explosion checks.
review-comparison.png — before/after and exposed-surface review sheet.
PNG renders — assembled, rear, top, left, exposed valley, exposed rear and exploded.

REPRODUCE
blender -b -t 4 -P reconstruct.py -- --out /your/output/directory --render
python validate_glb.py /your/output/directory/aj133-na-exterior-r01.glb
The --render flag is optional. CPU Cycles is used; no denoiser or add-ons needed.
Render studio is outside the exported engine root. No third-party reference
images, PDF manuals, credentials or existing application code are bundled.

WHAT THIS STUDY IMPROVES
Separate bank head/cam-cover silhouettes and visible sealing boundaries.
RH twin PCV caps, separate LH oil filler and approximate external breather curves.
NA intake plenum/runner envelope with rear actuator silhouettes, no supercharger.
Layered plate cooler and sealing layer located in the valley.
Bank-specific manifolds and separate shaped shield meshes.
Deep skirt block/sump, separate rear casting face and rear seal carrier.
Bellhousing envelope for context only; remove it in Blender to inspect rear face.

ACCURACY LIMITS
The assembly architecture is reference-based; detailed geometry is approximate.
The script does not trace or recover exact casting profiles from CAD. Casting ribs,
cover molding, port spacing, material finish and thicknesses are visual estimates.
No plug meshes, gallery drillings, drain openings or fastener patterns are invented.
Unverified gallery, rear head-plug, vacuum-pump and sensor locations are anchor
empties only, not physical fittings. A central crankshaft seal aperture is modeled;
this must not be interpreted as an oil-gallery opening or a source diagnosis.
Rear seal carrier shape is a generic interpretation of catalogue illustrations;
the engine-serial-specific version is not selected. The bellhousing is explicitly
an UNVERIFIED_ENVELOPE, not a transmission casting or validated clearance model.
PCV hose curves are illustrative; no hidden separator or fluid flow is modeled.
No oil runoff, borescope insertion path or installed-engine clearance is validated.
No internal rotating engine components are included.

ASSET CONTRACT FOR A FUTURE VIEWER ADAPTER (NOT IMPLEMENTED)
GLB: metres, +X vehicle right, +Y up, +Z rear. Scale is estimated, not measured.
19 named assembly groups map through extras.assembly_key to the existing nine UI
assembly keys. Per-group extras.explode_vector_gltf is an illustrative displacement
in GLB axes, not a service removal direction. Meshes are merged by material within
each group only, retaining independent visibility and per-group material cloning
for opacity. Do not mutate cached shared GLTF materials to set transparency.
12 anchor__<diagnostic-id> empties retain the existing diagnostic IDs. Anchors are
children of their component groups; a future adapter should derive world positions
from those nodes so labels follow an exploded assembly. Unverified anchors stay
regional placeholders and must not become verified location claims.
The live UI and controls have not been changed. No application integration is
included; that remains a separate review/approval step.

REFERENCES
JLR NP10-V8JLR 04/2009 training manual, pages 2-12, 2-30, 2-44, 2-49/50,
2-54 and 3-32. https://www.billswebspace.com/5.0V8.pdf
JLR Classic L320 NA catalogue: block P0190547-07, head P0190560-04,
exhaust P0190562-03, cooler P0190565-02, covers P0190624-05.
Full source URLs are retained in evidence-manifest.json.
These sources do not establish all 2012 casting revisions or service access.
