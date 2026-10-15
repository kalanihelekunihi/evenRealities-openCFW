#!/usr/bin/env python3
"""Link collision-free foundation C into the Apollo Main source candidate."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/foundation-integration-round858'
audit=json.loads((out/'receipt.json').read_text())
base_receipt=json.loads((root/'build/c-firmware/main-source-audit-round857/link-receipt.json').read_text())
base=root/base_receipt['linked_object']
excluded={'freertos_ready/tasks_subset.c','freertos_resume/tasks_resume.c','wsf_timer/wsf_timer_stop.c'}
objects=[]
for r in audit['results']:
 assert r['status']=='PASS'
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 if any(r['source'].endswith(x) for x in excluded):continue
 objects.append(root/r['object'])
assert len(objects)==37
providers=defaultdict(list)
for obj in [base,*objects]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):providers[f[-1]].append(obj.name)
collisions={name:owners for name,owners in providers.items() if len(owners)>1}
assert not collisions,collisions
linked=out/'apollo-main-foundation-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(o) for o in objects],'-o',str(linked)],check=True)
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
before=set(base_receipt['unresolved']);after=set(imports)
receipt={'round':858,'status':'PASS_RELOCATABLE_ONLY','component':'Apollo Main foundation source integration',
         'prior_source_units':1157,'new_source_units':len(objects),'excluded_collision_sources':sorted(excluded),
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'unresolved':imports,
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Excluded foundation variants require source-level provider selection',
                  'Native coverage, final layout, startup, image equality, and device execution remain open']}
(out/'link-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_FOUNDATION_SOURCE_RELOCATABLE',len(objects),len(before-after),len(after-before),len(imports))
