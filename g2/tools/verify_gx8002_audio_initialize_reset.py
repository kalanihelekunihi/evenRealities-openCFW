# SPDX-License-Identifier: MIT
"""Compose decoded initializer with decoded reset, for uniform initial MMIO."""
import json,subprocess
from itertools import product
from build_gx8002_audio_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from build_gx8002_audio_reset_candidate import build as reset_build,OFFSET,ADDRESS
from verify_gx8002_audio_reset import execute as reset_execute,expected as reset_expected,REGS,BASE
from execute_gx8002_audio_initialize import execute
from verify_gx8002_audio_initialize import oracle
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();reset=reset_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Nested reset stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd214','--stop-address=0xdf10',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-initialize/gain.disassembly.txt').read_text());reset_new=decode((ROOT/'build/gx8002-board/audio-reset-candidate.disassembly.txt').read_text());cases=0
    for seed,delay,mask,present in product((0,0xffffffff,0xa5a5a5a5),(0,1,7),(0,1,2,4,7),range(32)):
        def hook(code,entry):
            def run(memory):
                if any(memory.get(BASE+off,seed)!=seed for off in REGS):raise ValueError('Reset initial MMIO assumption')
                trace,state,result,status=reset_execute(code,entry,seed,'latched',delay)
                if result!=0 or status!='return':raise ValueError('Nested reset completion')
                return trace,state
            return run
        callbacks=tuple(0x10300000+4*i if present&(1<<i) else 0 for i in range(5))
        args=(callbacks,seed,mask,7,seed&15)
        a=execute(old,0xdd70,*args,reset_hook=hook(old,OFFSET));b=execute(new,0x102047e4,*args,reset_hook=hook(reset_new,ADDRESS))
        reset_trace,reset_state,result,status=reset_expected(seed,'latched',delay)
        if result!=0 or status!='return':raise ValueError('Reset oracle completion')
        wanted=oracle(*args,reset_effects=(reset_trace,reset_state))
        if a!=wanted or b!=wanted:raise ValueError('Nested initializer/reset independent oracle mismatch')
        if len(a[1])<60:raise ValueError('Reset instructions not represented')
        cases+=1
    return {'candidate':candidate,'reset_candidate':reset,'nested_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded reset called in separate frame with resulting MMIO propagated to initializer. Independent ordered-effect oracle and all32 callback-presence combinations. Uniform initial MMIO only; delayed completion0/1/7 polls. Other helpers/config callback remain modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-initialize-reset-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_cases'])
