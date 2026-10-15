#!/usr/bin/env python3
"""Compile current Ambiq renderer C and trial-link it to Apollo audio C."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
srcdir=root/'components/main/ambiq_buffer_handlers_candidate_20261014'
audio=root/'build/c-firmware/audio-source-coherence-round855/all-audio-source.o'
out=root/'build/c-firmware/ambiq-audio-integration-round856';out.mkdir(parents=True,exist_ok=True)
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
       '-std=c11','-ffreestanding','-fno-builtin','-O2',
       '-I'+str(root/'components/bootloader/filesystem/freestanding_include'),
       '-I'+str(root/'analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include')]
def compile_one(src):
 obj=out/(src.stem+'.o');p=subprocess.run(flags+['-c',str(src),'-o',str(obj)],capture_output=True,text=True)
 return {'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'object':str(obj.relative_to(root)) if p.returncode==0 else None,
         'status':'PASS' if p.returncode==0 else 'FAIL','diagnostic':p.stderr[:1200]}
sources=sorted(srcdir.glob('*.c'))
with ThreadPoolExecutor(max_workers=8) as pool:results=sorted(pool.map(compile_one,sources),key=lambda x:x['source'])
fail=[x for x in results if x['status']=='FAIL']
objects=[root/x['object'] for x in results if x['status']=='PASS']
providers=defaultdict(list)
for obj in [audio,*objects]:
 for line in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(obj)],text=True).splitlines():
  f=line.split()
  if len(f)>=3 and f[-2].upper() in ('B','C','D','R','T'):
   providers[f[-1]].append(obj.name)
collisions={k:v for k,v in providers.items() if len(v)>1}
result={'round':856,'component':'Apollo Main Ambiq renderer integration','source_count':len(results),
        'compiled':len(objects),'failed':len(fail),'compile_failures':fail,
        'strong_provider_collisions':collisions,'results':results,'whole_image_complete':False}
if not fail and not collisions:
 linked=out/'audio-ambiq-source.o'
 p=subprocess.run(['arm-none-eabi-ld','-r',str(audio),*[str(x) for x in objects],'-o',str(linked)],capture_output=True,text=True)
 result['link_status']='PASS' if p.returncode==0 else 'FAIL';result['link_diagnostic']=p.stderr[:2000]
 if p.returncode==0:
  u=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()]
  prior=json.loads((audio.parent/'all-audio-link.json').read_text())
  before=set(prior['unresolved']);after=set(u)
  result['resolved_prior_imports']=sorted(before-after)
  result['new_lower_imports']=sorted(after-before)
  result['unresolved_count']=len(u);result['unresolved']=u;result['linked_object']=str(linked.relative_to(root));result['linked_sha256']=hashlib.sha256(linked.read_bytes()).hexdigest()
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print('AMBIQ_AUDIO_INTEGRATION',len(objects),len(fail),len(collisions),result.get('link_status'),result.get('unresolved_count'))
for f in fail[:12]:print(f['source'],f['diagnostic'].splitlines()[0] if f['diagnostic'] else '')
for name,units in list(collisions.items())[:12]:print('COLLISION',name,units)
