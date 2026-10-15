#!/usr/bin/env python3
"""Select collision-free non-UART audio C, including additive successor bodies."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/audio-non-uart-round861'
audit=json.loads((out/'audit.json').read_text())
base=root/'build/c-firmware/wsf-timer-helpers-round860/apollo-main-wsf-timer-source.o'
excluded={'uart_tx_offline/am_hal_uart.c','transition_producers_offline/producers.c'}
objects=[]
for r in audit['results']:
 assert r['status']=='PASS'
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 if any(r['source'].endswith(x) for x in excluded):continue
 objects.append(root/r['object'])
assert len(objects)==191
providers=defaultdict(list)
for obj in [base,*objects]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):providers[f[-1]].append(obj.name)
collisions={name:owners for name,owners in providers.items() if len(owners)>1}
assert not collisions,collisions
linked=out/'apollo-main-expanded-audio-source.o'
link=subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(o) for o in objects],
                     '-o',str(linked)],capture_output=True,text=True)
assert link.returncode==0,link.stderr[:2000]
before={line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
after=set(imports)
receipt={'round':861,'status':'PASS_RELOCATABLE_ONLY','component':'Apollo Main expanded audio C source set',
         'prior_source_units':1196,'new_source_units':len(objects),
         'excluded_collision_sources':sorted(excluded),
         'selection_notes':['codec_request_offline/hal_bridge.c includes the sealed UART HAL source and adds codec_hal_blocking',
                            'transition_snapshot_offline/producers.c is the additive successor to transition_producers_offline/producers.c'],
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'unresolved':imports,
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'link_warnings':link.stderr.splitlines(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Selected C source set is not an authenticated complete native catalogue',
                  'Final image placement, startup, byte equality, and device execution remain open']}
(out/'link-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_AUDIO_NON_UART_RELOCATABLE',len(objects),len(before-after),len(after-before),len(imports))
