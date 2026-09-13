# SPDX-License-Identifier: MIT
"""Single timer setup execution sharing slot, IRQ and channel memory effects."""
import json,subprocess
from verify_gx8002_timer_initialize_gate import verify as qualify
from verify_gx8002_timer_initialize import execute,expected,ROOT,decode
from verify_gx8002_timer_channel_initialize import execute as channel,expected as channel_expected
from compare_gx8002_memset import execute as fill
from compare_gx8002_irq import execute as irq
from verify_gx8002_power_initialize import word

def verify():
    evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def program(path):return decode(subprocess.check_output([pre,'-d',str(ROOT/path)],text=True))
    outer=program('build/gx8002-board/timer-initialize-candidate.elf')
    inner=program('build/gx8002-board/timer-channel-initialize-candidate.elf')
    memset=program('build/gx8002-source-candidate/memset/memset.elf')
    irq_code=program('build/gx8002-source-candidate/irq/irq.elf');cases=0
    for hz in (0,999999,1024000,24576000,0xffffffff):
      for pattern in (0x55,0xaa,0xff):
        state={a:pattern for a in range(0x20026d80,0x20026f70)};before=state.copy();events=[]
        def write(address,value):word(state,address,value);events.append(('write',address,value))
        def helper(target,args,value):
            events.append(('call',target,*args))
            if target==0x102099cc:
                r=fill(memset,target,*args,seed=pattern)
                for address,width,v in r['trace']:
                    for i in range(width):state[address+i]=(v>>(8*i))&255
                return r['result']
            if target==0x1002553c:
                assert all(state[a]==0 for a in range(0x20026d84,0x20026eec))
                for effect in irq(irq_code,target,*args,enable=0x100254ac):
                    if effect==('enable',14):
                        for address,v in irq(irq_code,0x100254ac,14):write(address,v)
                    else:write(*effect)
            if target==0x100257b8:
                assert word(state,0x20026f64)==0x100258c4 and word(state,0xe000e100)==1<<14
                channel(inner,target,hz,pattern,write_hook=write)
            return value
        assert execute(outer,0x100257e8,hz,pattern,helper,write)==expected(hz)
        wanted=[]
        for event in expected(hz):
            wanted.append(event)
            if event==('call',0x1002553c,14,0x100258c4,0):wanted.extend([('write',0x20026f64,0x100258c4),('write',0x20026f68,0),('write',0xe000e100,1<<14)])
            if event==('call',0x100257b8):wanted.extend(e for e in channel_expected(hz) if e[0]=='write')
        assert events==wanted
        for address,value in before.items():
            if 0x20026d84<=address<0x20026eec:assert state[address]==0
            elif 0x20026f64<=address<0x20026f6c:continue
            else:assert state[address]==value
        cases+=1
    return {'evidence':evidence,'shared_state_cases':cases,'source_admitted':False,'limits':['One outer execution applies decoded memset, IRQ registration/enable, channel and outer MMIO effects to shared byte memory. Gate/frequency values remain scripted here and separately composed in prerequisites. Hardware delivery/timing and system caller remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-shared.json').write_text(json.dumps(r,indent=2)+'\n');print(r['shared_state_cases'])
