#!/usr/bin/env python3
"""Link current Main C with audio/render using prior selected formatter variant."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/main-source-audit-round857'
prior=root/'build/c-firmware/ambiq-audio-integration-round856/receipt.json'
audit=json.loads((out/'receipt.json').read_text());before=json.loads(prior.read_text())
selection_receipt=json.loads((root/'build/c-firmware/root-main-round585/receipt.json').read_text())
selected_text=str(selection_receipt['images']['apollo_main'])
native='full_formatter_native_candidate/'
outer='full_formatter_outer_candidate/'
for name in ('engine','entry','float_render','format_parser','fp_primitives','integer_cursor','integer_render','memclr4','termination'):
 assert native+name+'.c' in selected_text,name
assert outer+'vformat.c' in selected_text
excluded={outer+n+'.c' for n in ('float_bridge','float_render','fp_primitives','general_format')}
base=root/before['linked_object']
units=[]
for r in audit['results']:
 assert r['status']=='PASS'
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 if any(r['source'].endswith(x) for x in excluded):continue
 units.append(root/r['object'])
providers=defaultdict(list)
for obj in [base,*units]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):providers[f[-1]].append(obj.name)
collisions={name:owners for name,owners in providers.items() if len(owners)>1}
assert not collisions,collisions
linked=out/'apollo-audio-render-main-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(p) for p in units],'-o',str(linked)],check=True)
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
prior_imports=set(before['unresolved']);current=set(imports)
result={'round':857,'status':'PASS_RELOCATABLE_ONLY','component':'Apollo Main audio/render/main C source set',
        'prior_source_units':992,'new_source_units':len(units),'excluded_alternative_sources':sorted(excluded),
        'selection_evidence':'g2/build/c-firmware/root-main-round585/receipt.json',
        'selection_evidence_sha256':hashlib.sha256((root/'build/c-firmware/root-main-round585/receipt.json').read_bytes()).hexdigest(),
        'resolved_prior_imports':sorted(prior_imports-current),'new_lower_imports':sorted(current-prior_imports),
        'unresolved_count':len(imports),'unresolved':imports,'linked_object':str(linked.relative_to(root)),
        'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'strong_provider_collisions':0,
        'whole_image_complete':False,'hardware_proof':False}
(out/'link-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS_MAIN_SOURCE_RELOCATABLE',len(units),len(prior_imports-current),len(current-prior_imports),len(imports))
