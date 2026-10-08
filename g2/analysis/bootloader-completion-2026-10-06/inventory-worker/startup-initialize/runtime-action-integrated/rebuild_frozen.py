#!/usr/bin/env python3
"""Rebuild frozen offline candidate without changing shared artifacts."""
from pathlib import Path
import argparse,hashlib,json,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
h=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
m=json.loads((a.snapshot/'input-hashes.json').read_text());objects=[]
for x in m['inputs']:
 f=a.snapshot/x['path'];assert h(f)==x['sha256']
 # Assembly STT_FILE symbols derive from linker input basenames.
 stage=a.output.parent/'rebuild-inputs'/str(len(objects))/Path(x['original']).name
 stage.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,stage);objects.append(str(stage))
ld=a.snapshot/'source/runtime-action-integrated/module-bounded-kept.ld'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-T',str(ld),'-o',str(a.output),*objects],check=True)
assert h(a.output)==m['elf_sha256'],h(a.output)
print('PASS exact candidate rebuild',m['elf_sha256'])
