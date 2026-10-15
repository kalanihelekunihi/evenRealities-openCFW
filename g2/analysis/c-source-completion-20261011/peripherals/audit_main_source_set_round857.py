#!/usr/bin/env python3
"""Audit non-Ambiq Main C candidates against current Apollo audio/render source."""
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
main=root/'components/main';ambiq=main/'ambiq_buffer_handlers_candidate_20261014'
base=root/'build/c-firmware/ambiq-audio-integration-round856/audio-ambiq-source.o'
out=root/'build/c-firmware/main-source-audit-round857';out.mkdir(parents=True,exist_ok=True)
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
       '-std=c11','-ffreestanding','-fno-builtin','-O2',
       '-I'+str(root/'components/bootloader/filesystem/freestanding_include'),
       '-I'+str(root/'analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include')]
sources=sorted(p for p in main.glob('*/*.c') if p.parent!=ambiq)
def compile_one(src):
 rel=src.relative_to(main);obj=out/(rel.parent.name+'__'+rel.stem+'.o')
 p=subprocess.run(flags+['-c',str(src),'-o',str(obj)],capture_output=True,text=True)
 return {'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'object':str(obj.relative_to(root)) if p.returncode==0 else None,
         'status':'PASS' if p.returncode==0 else 'FAIL','diagnostic':p.stderr[:1300]}
with ThreadPoolExecutor(max_workers=8) as pool:results=sorted(pool.map(compile_one,sources),key=lambda x:x['source'])
objects=[root/x['object'] for x in results if x['status']=='PASS']
providers=defaultdict(list)
for obj in [base,*objects]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):
   providers[f[-1]].append(obj.name)
collisions={k:v for k,v in providers.items() if len(v)>1}
result={'round':857,'component':'Apollo Main non-Ambiq C source candidates',
        'source_count':len(results),'compiled':len(objects),'failed':len(results)-len(objects),
        'strong_provider_collisions':collisions,'results':results,
        'whole_image_complete':False,'selected_image_link':False}
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print('MAIN_SOURCE_AUDIT',len(results),len(objects),result['failed'],len(collisions))
for r in results:
 if r['status']=='FAIL':print('FAIL',r['source'],r['diagnostic'].splitlines()[0] if r['diagnostic'] else '')
for name,units in list(sorted(collisions.items()))[:30]:print('COLLISION',name,','.join(units))
