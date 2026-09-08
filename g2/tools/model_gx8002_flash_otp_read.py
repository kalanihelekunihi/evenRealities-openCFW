#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Expected OTP read effects; finite trace generation is not hardware proof."""
from model_gx8002_flash_otp_write import MASK,STATE

def expected(offset,buffer,length,size,base,stride,flags,manufacturer,width=3,delay=0,summarize_receive=False):
    trace=[['read',STATE+12,0x20028000],['read',0x20028014,0x20028100],['read',0x20028110,flags]]
    if not length:return MASK,trace
    trace.append(['read',0x20028108,size])
    if ((offset+length)&MASK)>size:return MASK,trace
    trace.extend([['read',0x20028100,base],['read',0x20028104,stride],['read',0x20028006,manufacturer]])
    if manufacturer not in (0x5e,0x85):return MASK,trace
    address=(base+offset+(flags&7)*stride)&MASK;remaining=length;done=0;encodes=0
    def call(target,*args):trace.append(['call',target,list(args)])
    def write(a,v):trace.append(['write',a,v])
    def writes(rows):
        for off,v in rows:write(0xa2000000+off,v)
    def encode():
        nonlocal encodes
        call(0x10023b8c,STATE+8,address,STATE+16);encodes+=1
    call(0x1002375c);write(STATE+16,0x48);encode()
    while remaining:
        chunk=remaining if remaining&0x80000000 else min(remaining,32)
        if chunk>65536 and not summarize_receive:raise ValueError('finite trace limit: large signed chunk requires separate qualification')
        current_width=(width+(encodes%2))&MASK
        prefix=(current_width+2)&MASK
        if prefix>64:raise ValueError('finite trace limit: oversized prefix')
        trace.append(['read',STATE+8,current_width]);call(0x1002364c)
        writes([(8,0)]);write(0xa0300090,2)
        writes([(0x4c,0),(0x10,0),(0,0x407),(4,(current_width+1)&MASK),(0x18,0),(0xf4,0),(8,1)])
        for i in range(prefix):
            trace.extend([['read',0xa2000028,0]]*delay+[['read',0xa2000028,2]])
            value=0x48 if i==0 else (address+i*17)&255
            trace.append(['byte-read',(STATE+16+i)&MASK,value]);writes([(0x60,value)])
        writes([(0x10,1)]);call(0x10023670)
        writes([(8,0),(0x10,0),(0,0x807),(4,chunk-1),(0x18,0),(0x54,7),(0x4c,1),(8,1),(0x10,1),(0x60,0)])
        if summarize_receive:
            trace.append(['receive-span',(buffer+done)&MASK,chunk])
        else:
            for i in range(chunk):
                trace.extend([['read',0xa2000028,0]]*delay+[['read',0xa2000028,8]])
                value=(0x12348000+(done+i)*73)&MASK
                trace.append(['read',0xa2000060,value]);trace.append(['byte-write',(buffer+done+i)&MASK,value&255])
        call(0x1002365c);writes([(8,0),(0x4c,0)]);write(0xa0300090,3);write(0xa0300090,1);writes([(8,1)])
        done+=chunk;remaining-=chunk;address=(address+chunk)&MASK;encode()
    call(0x1002375c)
    return done&MASK,trace
