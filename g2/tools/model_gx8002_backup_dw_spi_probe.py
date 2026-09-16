#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent SPI initialization transaction model; helper bodies excluded."""
from dataclasses import dataclass

MASTER=0x20017680
STATE=0x200176a4
REGS=0xa3000000

@dataclass(frozen=True)
class Case:
    tx_depth: int = 0
    rx_depth: int = 0
    tx_mismatch: int = 16
    rx_mismatch: int = 16
    status: tuple = (0,0)
    fifo_value: int = 0x12345678


def expected(case):
    if any(x not in (0,*range(2,258)) for x in (case.tx_mismatch,case.rx_mismatch)):
        raise ValueError('Mismatch must be zero (none) or an attempted value 2..257')
    trace=[]
    def write(a,v): trace.append(('write',a,v))
    def read(a,v): trace.append(('read',a,v)); return v
    def registers(): return read(STATE+4,REGS)
    write(STATE+4,REGS)
    write(STATE,MASTER)
    write(MASTER+24,STATE)
    write(MASTER,0)
    write(MASTER+4,1)
    write(MASTER+16,0x1000827c)
    write(MASTER+8,0x10008538)
    write(MASTER+12,0x100082a8)
    trace.append(('clock',14,1))
    write(registers()+8,0)
    write(registers()+44,78)
    depths=[]
    for field,offset,existing,mismatch in ((8,24,case.tx_depth,case.tx_mismatch),
                                          (12,28,case.rx_depth,case.rx_mismatch)):
        read(STATE+field,existing)
        result=existing
        if not existing:
            attempts=range(2,(mismatch or 257)+1)
            pointer=registers()+offset
            for value in attempts:
                write(pointer,value)
                pointer=registers()+offset
                read(pointer,value if value!=mismatch else value^1)
            result=(0 if mismatch==257 else mismatch) if mismatch else 258
            write(STATE+field,result)
            write(pointer,0)
        depths.append(result)
    write(0xa030008c,3)
    write(registers()+8,1)
    registers()
    statuses=iter(case.status)
    def status():
        try: value=next(statuses)
        except StopIteration: raise ValueError('Status script does not reach completion')
        return read(REGS+40,value)
    while status()&8:
        read(REGS+96,case.fifo_value)
    while status()&1:
        pass
    try:
        next(statuses)
        raise ValueError('Unused status script entries')
    except StopIteration:
        pass
    trace.append(('clock',14,0))
    write(STATE+16,0)
    write(STATE+20,0)
    trace.append(('register_master',MASTER))
    trace.append(('request_irq',16,0x10008288,STATE))
    return trace,tuple(depths)
