#!/usr/bin/env python3
"""Inventory global-provider collisions across all independently compiled audio units."""
from collections import defaultdict
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/audio-source-coherence-round855'
receipt=json.loads((out/'receipt.json').read_text())
objects=[root/r['object'] for r in receipt['results'] if r['status']=='PASS']
providers=defaultdict(list)
for obj in objects:
 text=subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True)
 for line in text.splitlines():
  fields=line.split()
  if len(fields)>=3:
   typ,name=fields[-2:]
   if typ.upper() in ('B','C','D','R','T','V','W'):
    providers[name].append({'source':obj.stem+'.c','type':typ})
collisions={name:units for name,units in providers.items() if sum(u['type'] not in ('W','V','w','v') for u in units)>1}
summary={'source_count':len(objects),'defined_symbol_count':len(providers),'strong_collisions':len(collisions),'collisions':collisions}
(out/'provider-collisions.json').write_text(json.dumps(summary,indent=2)+'\n')
print('AUDIO_PROVIDER_AUDIT',summary['source_count'],summary['defined_symbol_count'],summary['strong_collisions'])
for name,units in list(sorted(collisions.items()))[:30]:print(name,','.join(u['source'] for u in units))
