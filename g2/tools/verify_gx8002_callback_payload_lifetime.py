# SPDX-License-Identifier: MIT
"""Reproduce deferred response corruption after callback-stack reuse."""
import json,subprocess
from build_gx8002_app_command_callback import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_app_command_callback import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x129bc','--stop-address=0x12c88',str(path)],text=True));new=decode((ROOT/'build/gx8002-app-command-callback/candidate.disassembly.txt').read_text())
    rows=[]
    for code,entry in ((old,0x129bc),(new,0x10209430)):
        packet,reply=0x20040000,0x20026d5c
        seed={a+i:0xa5 for a,n in ((packet,28),(reply,32)) for i in range(n)};word(seed,packet+4,270);queued=[];snapshots=[]
        def helper(t,a,m,e,sp):
            if t==0x102083bc:
                queued.append((word(m,reply+16),word(m,reply+24)))
                snapshots.append(m.copy())
            elif t not in (0x10206c24,0x102049b0):raise ValueError('Unexpected helper')
            return 0
        ret,after,events=execute(code,entry,[packet],seed,helper)
        assert ret==('return',0) and len(queued)==1
        pointer,length=queued[0];memory=snapshots[0]
        assert length==1 and memory[pointer]==1 and 0x20070000-28<=pointer<0x20070000
        # A later frame owns this address after return. Model its ordinary write.
        memory[pointer]=0x7e
        assert memory[queued[0][0]]==0x7e
        rows.append({'entry':entry,'queued_pointer':pointer,'length':length,'during_enqueue':1,'after_stack_reuse':memory[pointer]})
    return {'candidate':candidate,'reproductions':rows,'source_admitted':False,'conclusion':'Both original and reconstructed callback retain a stack payload pointer. Deferred consumption can read overwritten data.','limits':['Queue and stack reuse modeled explicitly; no physical-device timing claim. Fix requires persistent source-owned payload storage and allocation qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-callback-payload-lifetime.json').write_text(json.dumps(r,indent=2)+'\n');print(r['conclusion'])
