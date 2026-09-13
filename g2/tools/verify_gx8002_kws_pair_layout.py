# SPDX-License-Identifier: MIT
"""Validate pair transform against independent standalone C builds."""
import json,subprocess
from itertools import product
from build_gx8002_kws_pair_candidate import build,ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute

def verify():
    evidence=build();out=ROOT/'build/gx8002-board'
    def text(name):
        elf=Elf32((out/name).read_bytes(),name);section=next(s for s in elf.sections if s['name']=='.text');return elf.contents(section)
    pair=text('kws-pair.elf');runner=text('kws-run.elf')
    assert len(runner)==192 and pair[20:212]==runner
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    combined=decode((out/'kws-pair.disassembly.txt').read_text());standalone=decode((out/'audio-completion-forward.disassembly.txt').read_text())
    assert combined[0x100260d2]==('lrw','r3, 0x20027b50',2)
    cases=0
    for target,private_data,status in product((0,0x10210000),(0,1,0x20060000,0xffffffff),(0,1,0x80000000,0xffffffff)):
        outcomes=[]
        for code in (combined,standalone):
            memory={};word(memory,0x20027b50,target);calls=[]
            def callback(destination,args,state,events):
                assert destination==target and args[:3]==[7,2,private_data]
                calls.append((destination,*args[:3]));word(state,0x20060000,0x98765432);return status
            result,after,events=execute(code,0x100260d0,[7,2,private_data],memory,callback)
            assert result[:2]==('return',0) and len(calls)==int(bool(target and private_data))
            outcomes.append((result,after,events,calls))
        assert outcomes[0]==outcomes[1];cases+=1
    return {'evidence':evidence,'runner_identical_to_standalone_bytes':192,'paired_callback_cases':cases,'source_admitted':False,'limits':['Pair transform preserves all independently linked runner bytes at same address; callback result/memory/calls match standalone. This proves transform fidelity, not runner algorithm correctness. Runner behavior and admission remain pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-pair-layout.json').write_text(json.dumps(r,indent=2)+'\n');print(r['paired_callback_cases'])
