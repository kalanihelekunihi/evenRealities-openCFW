#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Expected ordered effects for OTP write qualification (not an admission test)."""
MASK=0xffffffff
STATE=0x200264e4

def expected(offset,buffer,length,size,base,stride,flags,manufacturer,width=3):
    trace=[['read',STATE+12,0x20028000],['read',0x20028014,0x20028100],
           ['read',0x20028110,flags]]
    if not length:return MASK,trace
    trace.append(['read',0x20028108,size])
    if ((offset+length)&MASK)>size:return MASK,trace
    trace.extend([['read',0x20028100,base],['read',0x20028104,stride],['read',0x20028006,manufacturer]])
    if manufacturer not in (0x5e,0x85):return MASK,trace
    address=(base+offset+(flags&7)*stride)&MASK
    def call(target,*args):trace.append(['call',target,list(args)])
    call(0x1002375c);call(0x1002374c)
    trace.append(['write',STATE+16,0x42])
    call(0x10023b8c,STATE+8,address,STATE+16)
    # Encoder and transport mutate width to expose every required reload.
    width=(width+1)&MASK
    page_offset=address&255
    first=length if ((length+page_offset)&MASK)<=256 else 256-page_offset
    def transmit(done,chunk):
        nonlocal width
        trace.append(['read',STATE+8,width])
        call(0x10023e14,(width+1)&MASK,(buffer+done)&MASK,chunk)
        width=(width+1)&MASK
    transmit(0,first)
    if first!=length:
        done=first
        while done<length:
            call(0x10023b8c,STATE+8,(address+done)&MASK,STATE+16)
            width=(width+1)&MASK
            call(0x1002375c);call(0x1002374c)
            chunk=min(length-done,256)
            transmit(done,chunk);done+=chunk
    call(0x1002375c)
    return length&MASK,trace
