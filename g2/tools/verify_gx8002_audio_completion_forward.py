# SPDX-License-Identifier: MIT
"""Decoded audio forwarding callback arguments, conditions and ignored return."""
import json,subprocess
from itertools import product
from build_gx8002_audio_completion_forward_candidate import build,ROOT,sha,IMAGE_SHA
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute

def verify():
    candidate=build();directory=ROOT/'build/gx8002-board';path=directory/'padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x180e4','--stop-address=0x180f8',str(path)],text=True));new=decode((directory/'audio-completion-forward.disassembly.txt').read_text());cases=0
    for target,first,second,count,status in product((0,0x10210000,0x10028000),(0,0xffffffff),(0,0x20060000),(0,1,0xffffffff),(0,1,0x80000000,0xffffffff)):
        memory={};word(memory,0x20027b50,target)
        for code,entry in ((old,0x180e4),(new,0x100260d0)):
            calls=[]
            def callback(destination,parameters,state,events):
                assert destination==target and target and count and parameters[:3]==[first,second,count]
                calls.append(True)
                # Observable external effect must survive wrapper completion.
                word(state,0x20060000,0x12345678)
                return status
            outcome,after,events=execute(code,entry,[first,second,count],memory,callback)
            assert outcome[:2]==('return',0) and not events
            assert len(calls)==int(bool(target and count))
            wanted=memory.copy()
            if calls:word(wanted,0x20060000,0x12345678)
            assert after==wanted
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded stock/source forwarding conditions, original three arguments, ignored callback return, retained callback memory effect and ABI checked. Callback implementation modeled. Candidate four bytes oversized; callback slot ownership/caller integration and hardware remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-completion-forward-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
