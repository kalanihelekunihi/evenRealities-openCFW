#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Aligned TX FIFO transaction model; no hardware or target admission."""
from dataclasses import dataclass
from model_gx8002_spi_transfer_alignment import Case as SetupCase,setup_trace,STATE,REGS,TRANSFER,MESSAGE

@dataclass(frozen=True)
class Case(SetupCase):
    length: int = 4
    tx_depth: int = 16
    levels: tuple = (0,)
    status: tuple = (4,0)
    data: bytes = b'\x12\x34\x56\x78'


def expected(case):
    trace,width=setup_trace(case)
    if not case.transmit or width not in (1,2,4) or case.length%width or case.buffer%width:
        raise ValueError('TX model requires aligned supported-width TX')
    if len(case.data)<case.length: raise ValueError('Insufficient TX bytes')
    trace.extend([('read',STATE+4,REGS),('write',STATE+32,0),('write',REGS+8,0),
                  ('read',STATE+4,REGS),('write',REGS+16,1),
                  ('read',STATE+4,REGS),('write',REGS+76,0),
                  ('read',STATE+4,REGS),('write',REGS+8,1)])
    remaining=case.length//width
    offset=0
    levels=iter(case.levels)
    while remaining:
        try: level=next(levels)
        except StopIteration: raise ValueError('FIFO script exhausted')
        free=case.tx_depth-(level&(case.rx_depth*2-1))
        if free<0: raise ValueError('Negative FIFO space outside initial model')
        count=min(remaining,free)
        trace.extend([('read',STATE+4,REGS),('read',REGS+32,level),
                      ('read',STATE+8,case.tx_depth),('write',REGS+4,(count-1)&0xffffffff)])
        for i in range(count):
            address=case.buffer+offset+i*width
            value=int.from_bytes(case.data[offset+i*width:offset+(i+1)*width],'little')
            read_kind={1:'read8',2:'read16',4:'read'}[width]
            if width==2:
                trace.extend([(read_kind,address,value),('read',STATE+4,REGS)])
            else:
                trace.extend([('read',STATE+4,REGS),(read_kind,address,value)])
            trace.append(('write',REGS+96,value))
        offset+=count*width
        remaining-=count
    if next(levels,None) is not None: raise ValueError('Unused FIFO script')
    trace.append(('read',STATE+4,REGS))
    statuses=iter(case.status)
    def status():
        try: value=next(statuses)
        except StopIteration: raise ValueError('Incomplete readiness script')
        trace.append(('read',REGS+40,value))
        return value
    while not status()&4: pass
    while status()&1: pass
    if next(statuses,None) is not None: raise ValueError('Unused readiness script')
    trace.extend([('read',STATE+4,REGS),('read',TRANSFER+24,MESSAGE),('write',REGS+8,0),
                  ('read',STATE+16,MESSAGE),('write',0xa030008c,3),('clock',14,0),
                  ('write',STATE+16,0),('write',STATE+20,0)])
    return trace,0
