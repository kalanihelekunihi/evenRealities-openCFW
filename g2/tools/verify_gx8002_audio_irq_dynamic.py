# SPDX-License-Identifier: MIT
"""Scripted changing IRQ status and callback publication qualification."""
import json,subprocess
from verify_gx8002_audio_irq import build,ROOT,IMAGE_SHA,sha,Elf32,decode,execute,BASE,STATE,MASK

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';wrapper=out/'padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17e5c','--stop-address=0x180e4',str(wrapper)],text=True));new=decode((out/'audio-irq.disassembly.txt').read_text());cases=0
    for seed in range(512):
        def change(memory,address,ordinal):
            if address in (BASE+0x100,BASE+0x104):
                # Deterministic by access, independent of instruction layout.
                value=(seed*0x9e3779b9+ordinal*0x45d9f3b+address)&MASK
                value^=value>>16
                memory[address]=value if seed&1 else memory[address]^value
        def callback(memory,kind,mask):
            memory[BASE+0x104]|=((seed+kind)*0x12345)&MASK
            memory[BASE+0x100]^=(seed*0x10203)&MASK
            # Publish/remove later callbacks and change subsequent addresses.
            for i in range(kind+1,4):memory[STATE+12+4*i]=0x10220000+4*i if (seed+i)&1 else 0
            for off in (0x124,0x148,0x168,0x128,0x14c,0x16c):memory[BASE+off]^=mask+seed
        args=(MASK,MASK,15,seed)
        actual=execute(new,0x10025e48,*args,read_hook=change,callback_hook=callback)
        assert actual==execute(old,0x17e5c,*args,read_hook=change,callback_hook=callback),seed
        cases+=1
    # Explicit initial polling termination: first, second, or third read.
    for ready_read in (1,2,3,4):
        def ready(memory,address,ordinal):
            if address==BASE+0x104:memory[address]=1<<24 if ordinal>=ready_read else 0
        actual=execute(new,0x10025e48,0,0,0,91,read_hook=ready)
        assert actual==execute(old,0x17e5c,0,0,0,91,read_hook=ready)
        assert len([e for e in actual[1] if e[0]=='read' and e[1]==BASE+0x104])==min(ready_read,3)
        cases+=1
    bits=(0,1,2,3,4,5,16,17,18,19,20)
    for combination in range(1<<len(bits)):
        mask=sum(1<<bit for i,bit in enumerate(bits) if combination&(1<<i))
        actual=execute(new,0x10025e48,mask,mask,15,91)
        assert actual==execute(old,0x17e5c,mask,mask,15,91)
        events=[e for e in actual[1] if e[0]=='callback'];expected=[]
        if mask&0x1c0000:expected.append(('callback',2,(mask>>18)&7))
        if mask&7:expected.append(('callback',0,mask&7,0x12340124,0x12340148,0x12340168))
        if mask&56:expected.append(('callback',1,(mask>>3)&7,*[0x12340000+off if mask&(1<<(i+3)) else 0 for i,off in enumerate((0x128,0x14c,0x16c))]))
        expected.append(('callback',3,(mask>>16)&3))
        assert events==expected
        assert [e[2] for e in actual[1] if e[0]=='write']==[1<<bit for bit in (18,19,20,0,1,2,3,4,5,16,17) if mask&(1<<bit)]
        assert actual[2][BASE+0x104]==0
        cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Read-index-driven status/enable changes and callback mutations preserve exact stock/source ordered traces and memory. Independent bounded initial status-poll oracle and all2048 interrupt-bit combinations with independent callback/acknowledgement oracle. Scripted interleavings do not prove physical interrupt timing or arbitrary concurrent writes.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-irq-dynamic.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
