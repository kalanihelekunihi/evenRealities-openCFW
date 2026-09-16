#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Aligned RX FIFO transaction model; physical timing remains unqualified."""
from dataclasses import dataclass
from model_gx8002_backup_spi_transfer_alignment import Case as SetupCase,setup_trace,STATE,REGS,TRANSFER,MESSAGE

@dataclass(frozen=True)
class Case(SetupCase):
    transmit: bool = False
    length: int = 4
    levels: tuple = (2,)
    words: tuple = (0x12345678,0xabcdef01)


def expected(case):
    trace,width=setup_trace(case)
    if case.transmit or width not in (1,2,4) or case.length%width or case.buffer%width:
        raise ValueError('RX model requires aligned supported-width receive')
    if not 0<case.rx_depth<0x80000000: raise ValueError('RX depth outside initial model')
    trace.extend([('read',STATE+4,REGS),('write',STATE+32,0),('write',REGS+8,0),
                  ('read',STATE+4,REGS),('write',REGS+16,1),
                  ('read',STATE+4,REGS),('write',REGS+76,0)])
    remaining=case.length//width
    levels=iter(case.levels)
    words=iter(case.words)
    cursor=case.buffer
    trace.append(('read',STATE+4,REGS))
    while remaining:
        chunk=min(remaining,case.rx_depth)
        trace.extend([('write',REGS+8,0),
                      ('read',STATE+12,case.rx_depth),('read',STATE+4,REGS),
                      ('write',REGS+4,chunk-1),('read',STATE+4,REGS),
                      ('write',REGS+8,1),('read',STATE+4,REGS),('write',REGS+96,0),('read',STATE+4,REGS)])
        pending=chunk
        while pending:
            try: level=next(levels)
            except StopIteration: raise ValueError('RX FIFO script exhausted')
            available=level&(2*case.rx_depth-1)
            if available>pending: raise ValueError('FIFO overrun outside initial model')
            trace.append(('read',REGS+36,level))
            for _ in range(available):
                try: value=next(words)
                except StopIteration: raise ValueError('RX data script exhausted')
                trace.extend([('read',REGS+96,value),
                              ({1:'write8',2:'write16',4:'write'}[width],cursor,value&((1<<(width*8))-1))])
                if width!=2:trace.append(('read',STATE+4,REGS))
                cursor+=width
            pending-=available
        remaining-=chunk
    if next(levels,None) is not None or next(words,None) is not None:
        raise ValueError('Unused RX script input')
    trace.extend([('read',TRANSFER+24,MESSAGE),('read',STATE+16,MESSAGE),('write',REGS+8,0),('write',0xa030008c,3),('clock',14,0),
                  ('write',STATE+16,0),('write',STATE+20,0)])
    return trace,0
