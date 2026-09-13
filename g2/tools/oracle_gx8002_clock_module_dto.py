# SPDX-License-Identifier: MIT
"""Independent DTO pulse and temporary clock/gate transaction model."""
MASK=0xffffffff

def expected(module,dto,enable,table,modules,registers):
    mmio=dict(registers);trace=[('lookup',module,0 if module in modules else MASK)]
    def rd(a):trace.append(('read',a,mmio[a]));return mmio[a]
    def wr(a,v):
        v&=MASK;mmio[a]=v;trace.append(('write',a,v))
        if a&255 in (0x1c,0x20):
            normal=(a&~255)+0x18;mmio[normal]=(mmio[normal]|v) if a&255==0x1c else mmio[normal]&~v&MASK
    def select(a,shift,v):
        trace.append(('set',a,shift,v,1));wr(a,(rd(a)&~(1<<shift))|(v<<shift))
    if module not in modules:return trace,mmio
    row=modules[module];ptr=row['dto']
    if not ptr or not table[ptr]:return trace,mmio
    base=0xa0010000 if module<10 else 0xa0300000;address=base+table[ptr];prior=rd(address)
    if dto==prior&0x1ffffff and enable==int(not(prior&(1<<27))):return trace,mmio
    high=row['gate_high_offset'];clock=row['clock_offset'];assert 0<=clock<32
    inhibited=(rd(base+0x18)>>high)&1 if high>=0 else 0
    if inhibited:wr(base+0x20,1<<high)
    source=base+(0x8c if module<10 else 0x88);fast=(rd(source)>>clock)&1
    if fast:select(source,clock,0)
    config=dto|(1<<26)|(int(enable==0)<<27);update=config|(1<<25)
    for value in (1<<26,0,1<<26,config,update,update,config):wr(address,value)
    if fast:select(source,clock,1)
    if inhibited:wr(base+0x1c,1<<high)
    return trace,mmio
