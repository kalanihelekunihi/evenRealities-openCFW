# SPDX-License-Identifier: MIT
"""Compose decoded callback publication, forwarding and shutdown clearing."""
import json,subprocess
from itertools import product
from verify_gx8002_audio_completion_owner import verify as owners,ROOT,sha
from verify_gx8002_audio_completion_forward import verify as qualify
from verify_gx8002_kws_initialize import execute as initialize
from verify_gx8002_stream_shutdown import execute as shutdown
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute
from build_transparent_image import Elf32

def verify():
    ownership=owners();evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');base=ROOT/'build/gx8002-source-candidate'
    init=decode(subprocess.check_output([pre,'-d',str(base/'kws-initialize/init.elf')],text=True));done_path=base/'stream-shutdown/stream-shutdown.elf';done=decode(subprocess.check_output([pre,'-d',str(done_path)],text=True));elf=Elf32(done_path.read_bytes(),'done');entry=next(s['value'] for s in elf.symbols() if s['name']=='LvpKwsDone')
    forward=decode((ROOT/'build/gx8002-board/audio-completion-forward.disassembly.txt').read_text());cases=0;calls=0
    for target,mode,private_data,result in product((0,0x10210000),(0,1,2,0xffffffff),(0,0x20060000),(0,0xffffffff)):
        returned,events=initialize(init,target,mode,result);assert returned==0
        publications=[event for event in events if event[0]=='publish'];assert publications==[('publish',0x20027b50,target)]
        memory={};word(memory,0x20027b50,publications[0][2])
        for phase in ('running','stopped'):
            observed=[]
            def callback(destination,args,state,trace):
                assert destination==target and args[:3]==[7,2,private_data]
                observed.append(True);return result
            outcome,memory,trace=execute(forward,0x100260d0,[7,2,private_data],memory,callback)
            assert outcome[:2]==('return',0) and not trace
            assert len(observed)==int(phase=='running' and bool(target and private_data));calls+=len(observed)
            if phase=='running':
                effects,cleared,returned=shutdown(done,entry,0,target,result)
                assert returned==0 and cleared==0 and effects[-1]==['write',0x20027b50,0]
                word(memory,0x20027b50,cleared)
        cases+=1
    assert cases==32 and calls==8
    return {'ownership':ownership,'evidence':evidence,'lifecycle_cases':cases,'forwarded_callbacks':calls,'source_admitted':False,'limits':['Decoded lifecycle publication/clear results handed through callback-slot memory to decoded forwarder. Lower driver effects modeled; asynchronous timing and shared driver execution not qualified. Candidate remains oversized and unregistered.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-completion-lifecycle.json').write_text(json.dumps(r,indent=2)+'\n');print(r['lifecycle_cases'],r['forwarded_callbacks'])
