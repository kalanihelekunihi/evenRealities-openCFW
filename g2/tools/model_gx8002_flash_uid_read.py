#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ordered UID effects, with explicit finite-model restriction on negative counts."""
MASK=0xffffffff

def expected(buffer,requested,actual,manufacturer,delay=0,summarize_receive=False):
    trace=[['read',0x200264f0,0x20028000],['byte-read',0x20028006,manufacturer&255]]
    if manufacturer&255 not in (0x85,0x5e):
        trace.append(['write',actual,0]);return MASK,trace
    signed=requested if requested<0x80000000 else requested-(1<<32)
    count=min(signed,16)&MASK
    trace.extend([['write',actual,count],['call',0x1002364c,[]]])
    for off,value in ((8,0),(0x4c,0),(0,0xc07),(4,(count-1)&MASK),(0x10,1),(0x18,0x40000),(0xf4,0),(8,1),(0x60,0x4b),(0x60,0),(0x60,0),(0x60,0),(0x60,0)):
        trace.append(['write',0xa2000000+off,value])
    if summarize_receive and count:
        trace.append(['receive-span',buffer,count])
        trace.append(['call',0x1002365c,[]])
        return 0,trace
    if count>16:raise ValueError('negative UID capacity requires separate large-loop qualification')
    for i in range(count):
        trace.extend([['read',0xa2000028,0]]*delay+[['read',0xa2000028,8]])
        word=(0x12348000+i*73)&MASK
        trace.extend([['read',0xa2000060,word],['byte-write',(buffer+i)&MASK,word&255]])
    trace.append(['call',0x1002365c,[]])
    return 0,trace
