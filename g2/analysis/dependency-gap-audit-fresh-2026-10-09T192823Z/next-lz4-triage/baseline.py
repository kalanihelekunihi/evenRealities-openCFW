from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=Path.cwd();E=Path('/Users/kalani/Repo/jimrandomh/g2-firmware-emulator')
sha=lambda b:hashlib.sha256(b).hexdigest()
imgs=[json.loads(x) for x in Path('g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines()];im=next(x for x in imgs if x['id']=='apollo_main:flash');b=Path(im['content_path']).read_bytes();assert sha(b)==im['content_sha256'];base=im['address_spaces'][0]['mappings'][0]['loaded_start'];rows=[]
for line in Path('g2/symbols/apollo_main.tsv').read_text().splitlines():
 c=line.split('\t')
 if c[0] in ['0x0054EE90','0x0054EF08','0x0054F338']:
  a,z=int(c[0],16),int(c[1],16);x=b[a-base:z-base];assert sha(x)==c[-1];rows.append({'start':hex(a),'end_exclusive':hex(z),'bytes':len(x),'sha256':sha(x),'symbol_classification':c[4:6]})
assert len(rows)==3
inputs=['AGENTS.md','g2/workflow/README.md','g2/workflow/state.json','g2/workflow/target.json','g2/docs/reference/libraries.md','g2/symbols/apollo_main.tsv','g2/analysis/source-opportunity-boundaries-successor-2026-10-09/REPORT.md','g2/analysis/source-dependency-next-ledger-2026-10-09/SOURCE-OPPORTUNITIES.md','g2/analysis/repository-goal-source-reconciliation-2026-10-09/REPORT.md','third-party/upstream/lvgl/src/libs/lz4/lz4.c','third-party/upstream/lvgl/src/libs/lz4/lz4.h','third-party/upstream/lvgl/src/libs/lz4/LICENSE.txt']
inputs=[R/p for p in inputs]+[E/p for p in ['AGENTS.md','src/g2emu/device.py','src/g2emu/stock_navigation_core.py','docs/stock-text-recipes.md']]
call=b[0x56192e-base:0x56193a-base]
r={'status':'PASS','image':im,'image_bytes_hash_verified':True,'selected_extents':rows,'selected_bytes':sum(x['bytes'] for x in rows),'navigation_call':{'address':'0x56192e','locked_bytes_hex':call.hex(),'emulator_expected_bytes_hex':'92f7f1f804003868e1f65efb','matches_emulator_profile':False},'input_hashes':{str(p):sha(p.read_bytes()) for p in inputs},'scope':'Static baseline only; no function/source equivalence, executable coverage increment, execution or current ownership vacancy established.'}
(O/'BASELINE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':'PASS','selected_bytes':r['selected_bytes'],'emulator_callsite_matches':False,'image_sha256':sha(b)},indent=2))
