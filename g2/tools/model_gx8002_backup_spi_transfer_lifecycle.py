#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Busy/empty-message transaction contract; FIFO paths deliberately not modeled."""
from dataclasses import dataclass
DEVICE=0x2002b000
MASTER=0x20027af0
STATE=0x20027b14
MESSAGE=0x2002c000

@dataclass(frozen=True)
class Case:
    active: int = 0


def expected(case):
    trace=[('read',DEVICE,MASTER),('read',MASTER+24,STATE),
           ('write',MESSAGE+24,0),('read',STATE+16,case.active),
           ('write',MESSAGE+8,DEVICE)]
    if not case.active:
        trace.extend([('write',STATE+16,MESSAGE),('clock',14,1),
                      ('write',0xa030008c,2),('read',STATE+16,MESSAGE),
                      ('read',MESSAGE,MESSAGE),
                      ('write',0xa030008c,3),('clock',14,0)])
    trace.extend([('write',STATE+16,0),('write',STATE+20,0)])
    return trace,0
