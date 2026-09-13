# SPDX-License-Identifier: MIT
"""Initializer ordered-effects oracle; helpers remain explicitly modeled."""
import json,subprocess
from itertools import product
from build_gx8002_audio_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_audio_initialize import execute,STATE
from verify_gx8002_memcpy_source import decode

def oracle(callbacks,seed,input_mask,output_mask,selector,reset_effects=None):
    memory={STATE+4*i:seed for i in range(7)}
    memory.update({0xa0a00000+off:seed for off in (0,4,12,0x28,0x2c,0x48,0x4c,0x100,0x10c)})
    for off in (0x28,0x2c,0x48,0x4c):memory[0xa0a00000+off]=(seed&~15)|selector
    trace=[('gate',3,1),('memset',STATE,0,28),('reset',)]
    for i in range(7):memory[STATE+4*i]=0
    if reset_effects is not None:
        reset_trace,reset_state=reset_effects
        trace.extend(tuple(event) for event in reset_trace)
        memory.update(reset_state)
    def read(a):trace.append(('read',a,memory[a]));return memory[a]
    def write(a,v):memory[a]=v;trace.append(('write',a,v))
    def bit(off,n,v):
        a=0xa0a00000+off;old=read(a);write(a,(old&~(1<<n))|(v<<n))
    bit(0,31,1);bit(0,29,1);write(0xa0a0010c,0)
    if not callbacks[1]:return 0xffffffff,trace,memory
    for index,offset in ((1,8),(2,16),(0,12),(3,20),(4,24)):
        if callbacks[index]:write(STATE+offset,callbacks[index])
    trace.append(('config',callbacks[1]));memory[STATE]=input_mask;memory[STATE+4]=output_mask
    trace.append(('irq',2,0x10025e48,0))
    if callbacks[0]:
        mask=read(STATE+4)
        for n in range(3):
            if mask&(1<<n):bit(0x100,n,1)
    mask=read(STATE)
    if mask&1:bit(12,9,1);bit(0,7,0)
    for flag,offsets,limit in ((2,(0x28,0x2c),2),(4,(0x48,0x4c),8)):
        if mask&flag:
            for off in offsets:
                if read(0xa0a00000+off)&15<limit:bit(off,9,1)
            bit(0 if flag==2 else 4,15 if flag==2 else 31,0)
    return 0,trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Initializer stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdd70','--stop-address=0xdf10',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-initialize/gain.disassembly.txt').read_text());cases=0
    for present,input_mask,output_mask,selector,seed in product(range(32),(0,1,2,4,7,0xffffffff),(0,1,2,4,7), (0,1,2,7,8,15),(0,0xa5a5a5a5)):
        callbacks=tuple(0x10300000+4*i if present&(1<<i) else 0 for i in range(5));args=(callbacks,seed,input_mask,output_mask,selector);wanted=oracle(*args)
        if execute(old,0xdd70,*args)!=wanted or execute(new,0x102047e4,*args)!=wanted:raise ValueError('Initializer effect oracle '+repr(args))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All callback-presence combinations and selector boundaries checked against independent ordered effects. Helper/reset/IRQ and config effects modeled; actual helper source composition still pending. No physical initialization claim.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
