#!/usr/bin/env python3
"""Link bounded non-experimental excluded audio candidates to Apollo Main."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/audio-excluded-dirs-round864'
audit=json.loads((out/'audit.json').read_text())
base=root/'build/c-firmware/audio-same-entry-aliases-round863/apollo-main-aliased-source.o'
gated={'power_vendor_candidate','uart_irq_source_candidate'}
objects=[];excluded=[]
for r in audit['results']:
 assert r['status']=='PASS'
 src=root/r['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['source_sha256']
 if src.parent.name in gated:excluded.append(r['source']);continue
 objects.append(root/r['object'])
assert len(objects)==82 and len(excluded)==13
linked=out/'apollo-main-expanded-selected-source.o'
p=subprocess.run(['arm-none-eabi-ld','-r',str(base),*[str(o) for o in objects],'-o',str(linked)],capture_output=True,text=True)
assert p.returncode==0,p.stderr[:2000]
before={line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
after=set(imports)
receipt={'round':864,'status':'PASS_BOUNDED_RELOCATABLE_ONLY','component':'Apollo Main additional audio source directories',
         'prior_source_units':1428,'new_source_units':len(objects),'excluded_evidence_gates':excluded,
         'resolved_prior_imports':sorted(before-after),'new_lower_imports':sorted(after-before),
         'unresolved_count':len(imports),'unresolved':imports,
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'link_warnings':p.stderr.splitlines(),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Peripheral power candidate has documented stock differences and remains excluded',
                  'UART IRQ composition still needs child/callback validation and remains excluded',
                  'Bounded source oracles do not establish full filesystem, scheduler, or device behavior',
                  'Final native catalogue, image placement, byte equality, and hardware execution remain open']}
(out/'link-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_AUDIO_ADDITIONAL_SOURCE',len(objects),len(before-after),len(after-before),len(imports),len(p.stderr.splitlines()))
