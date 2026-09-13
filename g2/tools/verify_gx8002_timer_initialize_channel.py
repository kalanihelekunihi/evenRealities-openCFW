# SPDX-License-Identifier: MIT
"""Compose decoded timer initializer and channel setup with ordered effects."""
import json,subprocess
from itertools import product
from verify_gx8002_timer_initialize import verify as qualify,execute,expected,ROOT,decode
from verify_gx8002_timer_channel_initialize import execute as channel,expected as channel_expected
from verify_gx8002_timer_channel_frequency_pll import verify as channel_qualify

def verify():
    evidence=qualify();dependency=channel_qualify()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    outer=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True))
    inner=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-channel-initialize-candidate.elf')],text=True))
    cases=0
    for first,second,seed in product((0,999999,1000000,1024000,12288000,24576000,0xffffffff),(0,1024000,24576000,0xffffffff),(0,0xffffffff)):
        nested=[];calls=[]
        def helper(target,args,value):
            calls.append((target,args))
            if target==0x100257b8:
                assert not args
                nested.extend(channel(inner,target,second,seed))
            return value
        trace=execute(outer,0x100257e8,first,seed,helper)
        assert trace==expected(first) and nested==channel_expected(second)
        assert calls==[(0x10025080,(23,1)),(0x10025210,(23,)),(0x102099cc,(0x20026d84,0,360)),(0x1002553c,(14,0x100258c4,0)),(0x100257b8,())]
        # Expand the call at its exact location to preserve cross-function order.
        actual=[]
        for event in trace:
            actual.append(event)
            if event==('call',0x100257b8):actual.extend(nested)
        wanted=expected(first);index=wanted.index(('call',0x100257b8))+1
        wanted[index:index]=channel_expected(second)
        assert actual==wanted;cases+=1
    return {'evidence':evidence,'channel_dependency':dependency,'composed_cases':cases,'source_admitted':False,'limits':['Decoded outer/channel call composition preserves ordered effects and independently varied frequency results between calls. Slot clear, interrupt registration and gate remain modeled; hardware and shared-state helper composition pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-channel.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
