# SPDX-License-Identifier: MIT
"""Independent register transaction model for the authenticated divider descriptors."""
MASK=0xffffffff

def expected(module,divider,table,modules,registers):
    mmio=dict(registers);trace=[('lookup',module,0 if module in modules else MASK)]
    def rd(a):trace.append(('read',a,mmio[a]));return mmio[a]
    def wr(a,v):
        v&=MASK;mmio[a]=v;trace.append(('write',a,v))
        if a&255 in (0x1c,0x20):
            normal=(a&~255)+0x18;mmio[normal]=(mmio[normal]|v) if a&255==0x1c else mmio[normal]&~v&MASK
    def select(a,shift,v):
        trace.append(('set',a,shift,v,1));wr(a,(rd(a)&~(1<<shift))|(v<<shift))
    if module not in modules:return trace,mmio
    row=modules[module];ptr=row['divider']
    if not ptr or not table[ptr]:return trace,mmio
    base=0xa0010000 if module<10 else 0xa0300000;address=base+table[ptr];shift=table[ptr+1];mask=table[ptr+2]|table[ptr+3]<<8
    field=(rd(address)>>shift)&mask;current=field+1 if field else 0;trace.append(('divider',current))
    if current==divider:return trace,mmio
    load=shift+mask.bit_length();reset=load+1;assert reset<32
    high=row['gate_high_offset'];clock=row['clock_offset'];assert 0<=clock<32
    inhibited=(rd(base+0x18)>>high)&1 if high>=0 else 0
    if inhibited:wr(base+0x20,1<<high)
    source=base+(0x8c if module<10 else 0x88);fast=(rd(source)>>clock)&1
    switch=fast and (module==6 or module>=10)
    if switch:select(source,clock,0)
    # Separate reads/writes preserve reset and load pulse ordering and unrelated bits.
    for clear,set_bits in ((1<<reset,0),(0,1<<reset),(mask<<shift,0),(0,(divider-1 if divider else 0)<<shift),(1<<load,0),(0,1<<load)):
        wr(address,(rd(address)&~clear)|set_bits)
    if switch:select(source,clock,1)
    if inhibited:wr(base+0x1c,1<<high)
    return trace,mmio
