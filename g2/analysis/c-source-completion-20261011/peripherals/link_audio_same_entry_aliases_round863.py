#!/usr/bin/env python3
"""Bind authenticated same-entry C aliases from excluded duplicate translation units."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
prior=root/'build/c-firmware/audio-provider-bundle-round862'
out=root/'build/c-firmware/audio-same-entry-aliases-round863';out.mkdir(parents=True,exist_ok=True)
receipt=json.loads((prior/'link-receipt.json').read_text())
audit=json.loads((prior/'audit.json').read_text())
base=root/receipt['linked_object']
def symbols(path):
 result={}
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(path)],text=True).splitlines():
  f=line.split()
  if len(f)>=3:result[f[-1]]=(f[0],f[-2])
 return result
base_symbols=symbols(base)
needed=set(receipt['unresolved'])
source_sha={r['source']:r['source_sha256'] for r in audit['results']}
selected={}
for rel in receipt['excluded_colliding_sources']:
 source=root/rel
 assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha[rel],rel
 obj=prior/(source.stem+'.o')
 defined=symbols(obj)
 by_addr=defaultdict(list)
 for name,(address,typ) in defined.items():by_addr[address].append(name)
 for name,(address,typ) in defined.items():
  if name not in needed:continue
  canonical=sorted(n for n in by_addr[address] if n in base_symbols and n!=name)
  assert canonical,(name,rel)
  chosen=canonical[0]
  candidate={'alias':name,'canonical':chosen,'source':rel,
             'source_sha256':source_sha[rel],'object_address':address,
             'object_type':typ}
  assert name not in selected or selected[name]['canonical']==chosen,(name,selected[name],candidate)
  selected[name]=candidate
assert len(selected)==116,len(selected)
rows=[selected[name] for name in sorted(selected)]
map_path=out/'same-entry-map.json';map_path.write_text(json.dumps(rows,indent=2)+'\n')
linked=out/'apollo-main-aliased-source.o'
args=['arm-none-eabi-ld','-r']+[f"--defsym={r['alias']}={r['canonical']}" for r in rows]+[str(base),'-o',str(linked)]
p=subprocess.run(args,capture_output=True,text=True)
assert p.returncode==0,p.stderr[:2000]
linked_symbols=symbols(linked)
for row in rows:
 assert linked_symbols[row['alias']]==linked_symbols[row['canonical']],row
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
after=set(imports)
assert not after&set(selected)
assert len(imports)==len(needed)-len(selected),(len(imports),len(needed),len(selected))
result={'round':863,'status':'PASS_SOURCE_BACKED_SAME_ENTRY_ALIAS_RELOCATABLE_ONLY',
        'component':'Apollo Main same-entry alias binding','prior_source_units':1428,
        'alias_count':len(rows),'alias_map':str(map_path.relative_to(root)),
        'alias_map_sha256':hashlib.sha256(map_path.read_bytes()).hexdigest(),
        'unresolved_before':len(needed),'unresolved_after':len(imports),
        'linked_object':str(linked.relative_to(root)),
        'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
        'link_warnings':p.stderr.splitlines(),'whole_image_complete':False,'hardware_proof':False,
        'gates':['Same-entry binding is proved only for compiled C object symbol addresses and names',
                 'Remaining excluded translation units duplicate already selected function bodies',
                 'Native equivalence, final image placement, and device execution remain unproven']}
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS_AUDIO_SAME_ENTRY_ALIASES',len(rows),len(imports))
