#!/usr/bin/env python3
"""Compile excluded audio candidate directories and inventory provider overlap."""
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
srcdir=root/'components/audio'
base=root/'build/c-firmware/audio-same-entry-aliases-round863/apollo-main-aliased-source.o'
out=root/'build/c-firmware/audio-excluded-dirs-round864';out.mkdir(parents=True,exist_ok=True)
dirs={'uart_irq_source_candidate','power_vendor_candidate','scheduler_delay_candidate',
      'classify_adapter_candidate','thread_new_source_candidate','event_wait_source_candidate',
      'file_backend_close_candidate','file_heap_free_candidate','file_sync_candidate',
      'file_pool_free_candidate','semihost_error_candidate'}
sources=sorted(p for name in dirs for p in (srcdir/name).glob('*.c'))
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
       '-std=c11','-ffreestanding','-fno-builtin','-O2']
def compile_one(src):
 rel=src.relative_to(srcdir);obj=out/(rel.parent.name+'__'+rel.stem+'.o')
 p=subprocess.run(flags+['-c',str(src),'-o',str(obj)],capture_output=True,text=True)
 return {'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'object':str(obj.relative_to(root)) if p.returncode==0 else None,
         'status':'PASS' if p.returncode==0 else 'FAIL','diagnostic':p.stderr[:1200]}
with ThreadPoolExecutor(max_workers=8) as pool:results=sorted(pool.map(compile_one,sources),key=lambda x:x['source'])
objects=[root/x['object'] for x in results if x['status']=='PASS']
providers=defaultdict(list)
for obj in [base,*objects]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):providers[f[-1]].append(obj.name)
collisions={k:v for k,v in providers.items() if len(v)>1}
result={'round':864,'component':'Apollo audio previously excluded candidate dirs audit',
        'source_count':len(results),'compiled':len(objects),'failed':len(results)-len(objects),
        'strong_provider_collisions':collisions,'results':results,
        'whole_image_complete':False,'selected_image_link':False}
(out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('AUDIO_EXCLUDED_AUDIT',len(results),len(objects),result['failed'],len(collisions))
for r in results:
 if r['status']=='FAIL':print('FAIL',r['source'],r['diagnostic'].splitlines()[0] if r['diagnostic'] else '')
for name,owners in list(sorted(collisions.items()))[:40]:print('COLLISION',name,','.join(owners))
