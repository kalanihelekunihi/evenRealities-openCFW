#!/usr/bin/env python3
"""Link collision-free old audio providers into current source-owned Apollo set."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/audio-provider-bundle-round862'
audit=json.loads((out/'audit.json').read_text())
base=root/'build/c-firmware/audio-non-uart-round861/apollo-main-expanded-audio-source.o'
colliding={owner for owners in audit['strong_provider_collisions'].values() for owner in owners if owner!=base.name}
objects=[];excluded=[]
for r in audit['results']:
 assert r['status']=='PASS'
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 obj=root/r['object']
 if obj.name in colliding:excluded.append(r['source']);continue
 objects.append(obj)
assert len(objects)==41 and len(excluded)==47
linked=out/'apollo-main-provider-bundle-source.o'
p=subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(o) for o in objects],'-o',str(linked)],capture_output=True,text=True)
assert p.returncode==0,p.stderr[:2000]
before={line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
after=set(imports)
receipt={'round':862,'status':'PASS_COLLISION_FREE_RELOCATABLE_ONLY','component':'Apollo Main older audio provider bundle',
         'prior_source_units':1387,'new_source_units':len(objects),'excluded_colliding_sources':excluded,
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'unresolved':imports,
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'link_warnings':p.stderr.splitlines(),'whole_image_complete':False,'hardware_proof':False,
         'gates':['47 overlapping alias/provider units need explicit source selection or decomposition',
                  'Native function coverage and remaining data/config imports remain incomplete',
                  'Final image placement, startup, byte equality, and hardware execution remain open']}
(out/'link-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_AUDIO_PROVIDER_BUNDLE',len(objects),len(before-after),len(after-before),len(imports),len(p.stderr.splitlines()))
