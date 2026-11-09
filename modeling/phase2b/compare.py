from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import json
out=Path('/workspace/output/aj133-phase2b');canvas=Image.new('RGB',(1680,1500),'#101c24');d=ImageDraw.Draw(canvas)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((35,24),'AJ133 / PHASE 2B REAR GEOMETRY REVIEW',font=font(28),fill='#e4eef0')
d.text((35,66),'SAME REAR CAMERA / SCALE   •   UNMEASURED RECONSTRUCTION   •   NO APPLICATION INTEGRATION',font=font(14),fill='#e6b67f')
items=[('PHASE 2 / preserved baseline','phase2-baseline-same-camera.png','Uniform rear envelopes; original fallback is unchanged.'),('PHASE 2B / rear refinement','rear-engine-hires.png','Stepped head shoulders, rear flange and carrier refinement.'),('REAR HEADS / surroundings hidden','rear-heads-isolated.png','Dark projections: approximate NA CPS envelopes, NOT gallery plugs.'),('REAR BLOCK / bellhousing hidden','rear-block-isolated.png','Documented plug source remains a regional annotation in the review.')]
for i,(title,file,caption) in enumerate(items):
 x=30+(i%2)*825;y=110+(i//2)*655
 d.rounded_rectangle((x,y,x+795,y+635),radius=5,fill='#192b35',outline='#3c535e');d.text((x+18,y+17),title,font=font(19),fill='#d7e8ed')
 im=ImageOps.contain(Image.open(out/file).convert('RGB'),(755,552));canvas.paste(im,(x+(795-im.width)//2,y+55+(552-im.height)//2));d.text((x+14,y+606),caption,font=font(12),fill='#acbfca')
d.text((35,1450),'Rear ball-plug locations and under-manifold closures remain unresolved. No plug map or service clearance is verified.',font=font(16),fill='#d4b48f')
canvas.save(out/'phase2-vs-phase2b.png')
(out/'comparison-camera.json').write_text(json.dumps({'position_gltf':[0,.36,1.8],'target_gltf':[0,.12,.28],'orthographic_scale':1.35,'resolution':[2000,1500],'hidden':['Bellhousing_Envelope'],'registration':'Common model datum; not measured CAD or photo registration'},indent=2))
