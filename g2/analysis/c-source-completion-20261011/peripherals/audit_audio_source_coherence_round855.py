#!/usr/bin/env python3
"""Compile every current Apollo audio C source independently; report exact failures.

This is an inventory audit, not a selected-image link or evidence of full coverage.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
sources=sorted((root/'components/audio/uart_thread_source_candidate').glob('*.c'))
out=root/'build/c-firmware/audio-source-coherence-round855';out.mkdir(parents=True,exist_ok=True)
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
       '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
       '-I'+str(root/'components/bootloader/filesystem/freestanding_include'),
       '-I'+str(root/'analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include')]
def compile_one(source):
 obj=out/(source.stem+'.o');result=subprocess.run(flags+['-c',str(source),'-o',str(obj)],capture_output=True,text=True)
 return {'source':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'object':str(obj.relative_to(root)) if result.returncode==0 else None,
         'status':'PASS' if result.returncode==0 else 'FAIL',
         'diagnostic':result.stderr[:1600] if result.returncode else ''}
with ThreadPoolExecutor(max_workers=8) as pool:
 results=sorted((f.result() for f in as_completed([pool.submit(compile_one,s) for s in sources])),key=lambda x:x['source'])
receipt={'round':855,'component':'Apollo audio C source inventory','total_sources':len(results),
         'compiled':sum(r['status']=='PASS' for r in results),'failed':sum(r['status']=='FAIL' for r in results),
         'selected_image_link':False,'whole_image_complete':False,'results':results}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('AUDIO_SOURCE_COMPILE_AUDIT',receipt['compiled'],receipt['failed'])
for result in results:
 if result['status']=='FAIL':print(result['source'],result['diagnostic'].splitlines()[0] if result['diagnostic'] else '')
