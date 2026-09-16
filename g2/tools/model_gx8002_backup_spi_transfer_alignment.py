#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Nonempty transfer setup and alignment-error contract; no FIFO execution yet."""
from dataclasses import dataclass
from model_gx8002_spi_transfer_lifecycle import DEVICE,MASTER,STATE,MESSAGE
TRANSFER=0x2002d000
CONFIG=0x2002e000
REGS=0xa3000000

@dataclass(frozen=True)
class Case:
    bits: int = 16
    length: int = 3
    buffer: int = 0x20030000
    transmit: bool = True
    control: int = 0x80000000
    divider: int = 10
    mode: int = 2
    rx_depth: int = 16


def setup_trace(case):
    if not 0<=case.bits<=32: raise ValueError('Width outside initial modeled domain')
    width=1 if case.bits<=8 else 2 if case.bits<=16 else 4
    bits=case.bits or 8
    tx=case.buffer if case.transmit else 0
    t=[('read',DEVICE,MASTER),('read',MASTER+24,STATE),('write',MESSAGE+24,0),
       ('read',STATE+16,0),('write',MESSAGE+8,DEVICE),('write',STATE+16,MESSAGE),
       ('clock',14,1),('write',0xa030008c,2),('read',STATE+16,MESSAGE),
       ('read',MESSAGE,TRANSFER+24),
       ('read',MESSAGE+8,DEVICE),('read',TRANSFER,tx),('write',STATE+20,TRANSFER),
       ('read',DEVICE+12,CONFIG)]
    if not tx: t.append(('read',TRANSFER+4,case.buffer))
    t.extend([('read',TRANSFER+8,case.length),('write',STATE+24,case.buffer),
              ('write',STATE+28,case.length),('read8',TRANSFER+13,case.bits)])
    if not case.bits: t.append(('write8',TRANSFER+13,8))
    t.extend([('write8',STATE+40,width),('read',TRANSFER,tx),
              ('read8',TRANSFER+13,bits),('read',CONFIG+4,case.control),
              ('read',STATE+4,REGS),('write',REGS+8,0),
              ('read',STATE+4,REGS),('read',CONFIG+12,case.mode),
              ('write',REGS+240,case.mode),('read',STATE+4,REGS),
              ('write',REGS,(bits-1)|case.control|(1024 if tx else 2048)),
              ('read',CONFIG+8,case.divider),('read',STATE+4,REGS),
              ('write',REGS+20,max(case.divider&65535,2)),
              ('read',STATE+4,REGS),('write',REGS+4,0),
              ('read',STATE+4,REGS),('write',REGS+76,0),
              ('read8',STATE+40,width),('read',STATE+28,case.length),
              ('read',STATE+12,case.rx_depth)])
    return t,width


def expected(case):
    trace,width=setup_trace(case)
    if case.length%width==0 and case.buffer%width==0:
        raise ValueError('Aligned transfer requires FIFO model')
    trace.extend([('write',0xa030008c,3),('clock',14,0),
                  ('write',STATE+16,0),('write',STATE+20,0)])
    return trace,0xffffffea
