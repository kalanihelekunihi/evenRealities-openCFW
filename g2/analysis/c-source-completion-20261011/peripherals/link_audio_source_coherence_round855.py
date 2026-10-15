#!/usr/bin/env python3
"""Relocatable link of every current Apollo audio C unit after compile audit."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/audio-source-coherence-round855'
compile_receipt=json.loads((out/'receipt.json').read_text())
assert compile_receipt['failed']==0 and compile_receipt['compiled']==compile_receipt['total_sources']
collisions=json.loads((out/'provider-collisions.json').read_text())
assert collisions['strong_collisions']==0
objects=[]
for unit in compile_receipt['results']:
 source=root/unit['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==unit['source_sha256'],source
 obj=root/unit['object'];assert obj.is_file(),obj
 objects.append(obj)
linked=out/'all-audio-source.o'
subprocess.run(['arm-none-eabi-ld','-r',*[str(o) for o in objects],'-o',str(linked)],check=True)
imports=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
providers=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(linked)],text=True).splitlines()]
for name in ('audio_ble_master_child_4bb25c','audio_ble_master_event_50393e','audio_ble_master_resolution_check_47ab6c'):
 assert name in providers and name not in imports,name
result={'round':855,'status':'PASS_RELOCATABLE_ONLY','component':'Apollo audio source set',
        'source_count':len(objects),'global_provider_count':len(set(providers)),
        'unresolved_count':len(imports),'unresolved':imports,
        'object':str(linked.relative_to(root)),'sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
        'whole_image_complete':False,'hardware_proof':False,
        'gates':['Directory source set is not an authenticated complete firmware source catalogue',
                 f'{len(imports)} unresolved cross-component, product, library, and runtime symbols remain',
                 'Final linker placement, startup, byte equality, and hardware execution remain unproven']}
(out/'all-audio-link.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS_AUDIO_SOURCE_RELOCATABLE_LINK',len(objects),len(imports))
