"""Embed local model, fallback and bundled Three.js into one offline HTML review file."""
import base64,json,subprocess,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--esbuild',required=True);a=p.parse_args()
source=Path(__file__).parent;out=Path(a.out);bundle=out/'review-bundle.js'
subprocess.run([a.esbuild,str(source/'review.js'),'--bundle','--format=iife','--minify','--legal-comments=inline','--outfile='+str(bundle)],check=True)
s=(source/'review-template.html').read_text()
for key,file in [('__MODEL__',out/'aj133-na-phase2b-r01.glb'),('__FALLBACK__',out/'fallback-phase2/aj133-na-exterior-r01.glb')]:s=s.replace(key,json.dumps(base64.b64encode(file.read_bytes()).decode()))
s=s.replace('__DATA__',(out/'diagnostic-data.json').read_text()).replace('__BUNDLE__',bundle.read_text().replace('</script','<\\/script'))
(out/'review.html').write_text(s)
print('Offline review:',(out/'review.html').stat().st_size,'bytes')
