#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent transaction contract for DW SPI setup; no target execution."""
from __future__ import annotations
from dataclasses import dataclass

MASK = 0xffffffff
DEVICE = 0x2002b000
FIXED_STATE = 0x20017670
OTHER_STATE = 0x2002c000

@dataclass(frozen=True)
class Case:
    bits: int = 0
    speed: int = 0
    state: int = 0
    owner: int = 0
    clock: int = 100000000
    format: int = 0
    mode_after_call: int = 0
    speed_after_call: int | None = None


def expected(case):
    """Return externally observable accesses and result, including helper effects.

    Cases require valid distinct device/state storage and a nonzero speed after
    the clock helper. The helper's body is not proven by this model.
    """
    if case.state not in (0, OTHER_STATE):
        raise ValueError('Unsupported state layout')
    trace = [('write16', DEVICE + 10, 0), ('read8', DEVICE + 9, case.bits)]
    if case.bits == 0:
        trace.append(('write8', DEVICE + 9, 8))
    trace.append(('read32', DEVICE + 12, case.state))
    state = case.state or FIXED_STATE
    if not case.state:
        trace.append(('read32', state, case.owner))
        if case.owner:
            return trace, MASK - 11
    trace.append(('read32', DEVICE + 4, case.speed))
    speed = case.speed
    if speed == 0:
        speed = 10000000
        trace.append(('write32', DEVICE + 4, speed))
    trace.append(('clock', 14, case.clock))
    if case.speed_after_call is not None:
        speed = case.speed_after_call
    if not 0 < speed <= MASK or not 0 <= case.clock <= MASK:
        raise ValueError('Invalid division domain')
    trace.append(('read32', DEVICE + 4, speed))
    # Round the rational clock/speed upward to an even divisor, then apply
    # target unsigned-word wrap. This differs from the C expression structure.
    rounded_up = (case.clock + speed - 1) // speed
    divider = (rounded_up + (rounded_up & 1)) & MASK
    control = 0x80000000 | ((case.format & 3) << 22) | ((case.mode_after_call & 3) << 8)
    trace.extend([('write32', state, DEVICE),
                  ('read8', DEVICE + 16, case.format),
                  ('read16', DEVICE + 10, case.mode_after_call),
                  ('write32', state + 4, control),
                  ('write32', state + 8, divider),
                  ('write32', state + 12, 2),
                  ('write32', DEVICE + 12, state)])
    return trace, 0
