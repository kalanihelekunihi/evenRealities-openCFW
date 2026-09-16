# SPDX-License-Identifier: MIT
"""Independent timer scheduling and ordered state access model."""
BASE=0x200174bc
MASK=0xffffffff

def expected(memory,times,callback):
    m=dict(memory);trace=[];ti=0
    def read(a):trace.append(('read',a,m[a]));return m[a]
    def write(a,v):m[a]=v&MASK;trace.append(('write',a,m[a]))
    for slot in range(10):
        a=BASE+36*slot
        if not read(a+28):continue
        now=times[ti];ti+=1;trace.append(('time',now));high=read(a+24)
        if now>>32<high:continue
        if now>>32==high and now&MASK<read(a+20):continue
        target=read(a);argument=read(a+4);trace.append(('callback',target,argument));callback(target,argument,m)
        interval=(read(a+8)*1000)&MASK;repeat=read(a+32)
        signed_interval=interval if interval<1<<31 else interval-(1<<32)
        due=(now+signed_interval)&((1<<64)-1)
        write(a+12,now);write(a+16,now>>32);write(a+20,due);write(a+24,due>>32)
        if not repeat:write(a+28,0)
    write(0xa0400000,read(0xa0400000)|1)
    return trace,m
