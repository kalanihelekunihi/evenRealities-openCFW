# SPDX-License-Identifier: MIT
"""Compose parameter updates with VAD selection and synchronous level mutation."""
import json,subprocess
from itertools import product
from verify_gx8002_vad_query_transitions import verify,execute,ROOT,decode


def check():
    transitions=verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x10990','--stop-address=0x10b54',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-audio-input-query-vad/index.disassembly.txt').read_text());cases=0
    noises=(0,3145727,3145728,6291455,6291456,20971520,20971521,0xffffffff)
    for noise,level,index,value in product(noises,(0,1,2,3,4,0xffffffff),(0,1,32,64,95,65535),(0,0xffffffff)):
        target=4 if noise<3145728 else 3 if noise<6291456 else 2 if noise<=20971520 else 1
        wanted=1 if target==1 else int(bool(value))
        for code,entry in ((old,0x10990),(new,0x10207404)):
            if execute(code,entry,noise,level,0xff,(value,value,value,index))!=wanted:raise ValueError('Complete query')
        cases+=1
    mutation_cases=0
    # Mutate after state acquisition, when both implementations must reread LEVEL.
    for noise,level,replacement in product(noises,(0,1,2,3,4,0xffffffff),(0,1,2,0xffffffff)):
        def mutation(target,current):return replacement if target==0xdd08 else current
        for code,entry in ((old,0x10990),(new,0x10207404)):
            if execute(code,entry,noise,level,0xa5,(0,0,0,95),mutation)!=int(replacement==1):raise ValueError('State-helper level mutation')
        mutation_cases+=1
    # Other helpers may change LEVEL; compare full instruction streams without
    # assuming an unchanged level across diagnostics or curve programming.
    for noise,level,target,replacement in product(noises,(0,1,4),(0xdd38,0x101b0,0xdbbc,0xdb80),(1,3,0xffffffff)):
        def mutation(called,current):return replacement if called==target else current
        a=execute(old,0x10990,noise,level,0xff,(0,0,0,0),mutation)
        b=execute(new,0x10207404,noise,level,0xff,(0,0,0,0),mutation)
        if a!=b:raise ValueError(('Programming mutation',noise,level,target,replacement))
        mutation_cases+=1
    return {'transitions':transitions,'complete_cases':cases,'mutation_cases':mutation_cases,'source_admitted':False,'limits':['Full level-update/result composition and selected synchronous level mutations pass. Driver bodies modeled; no asynchronous/timing qualification. Source admission pending.']}


if __name__=='__main__':
    report=check();(ROOT/'docs/research/gx8002-vad-query-complete.json').write_text(json.dumps(report,indent=2)+'\n');print(report['complete_cases'],report['mutation_cases'])
