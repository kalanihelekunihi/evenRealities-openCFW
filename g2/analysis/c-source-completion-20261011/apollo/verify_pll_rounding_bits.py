#!/usr/bin/env python3
"""Bounded stock raw-bit oracle for the selected PLL floor/round/ceil source."""
import hashlib
import json
import random
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/clock_pll_rounding.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == LOCKED


def source_bits(bits, operation):
    exponent = (bits >> 23) & 255
    shift = exponent - 126
    if shift <= 0:
        if operation == 'floor':
            if (bits << 1) & 0xffffffff:
                return 0xbf800000 if bits >> 31 else 0
        elif operation == 'round':
            return (bits & 0x80000000) | (0x3f800000 if shift == 0 else 0)
        else:
            if (bits << 1) & 0xffffffff:
                return 0x80000000 if bits >> 31 else 0x3f800000
    elif shift < 24:
        mask = 0x00ffffff >> shift
        if operation == 'floor':
            if bits >> 31:
                bits = (bits + mask) & 0xffffffff
        elif operation == 'round':
            bits &= ~(mask >> 1) & 0xffffffff
            bits = (bits + mask) & 0xffffffff
        else:
            if not bits >> 31:
                bits = (bits + mask) & 0xffffffff
        bits &= ~mask & 0xffffffff
    return bits


blob = STOCK.read_bytes()
rng = random.Random(0x427ca0)
values = [0, 0x80000000, 1, 0x80000001, 0x3f000000, 0xbf000000,
          0x3f7fffff, 0xbf7fffff, 0x3f800000, 0xbf800000,
          0x7f800000, 0xff800000, 0x7fc00001, 0xffc00001]
values.extend(rng.getrandbits(32) for _ in range(256))
entries = {'floor': 0x427ca0, 'round': 0x427da8, 'ceil': 0x427de0}
count = 0
for operation, entry in entries.items():
    for bits in values:
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x410000, 0x40000)
        cpu.mem_write(0x410000, blob)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.mem_map(0x500000, 0x1000)
        cpu.reg_write(UC_ARM_REG_R0, bits)
        cpu.reg_write(UC_ARM_REG_SP, 0x20008000)
        cpu.reg_write(UC_ARM_REG_LR, 0x500001)
        cpu.emu_start(entry | 1, 0x500000, count=2000)
        actual = cpu.reg_read(UC_ARM_REG_R0)
        expected = source_bits(bits, operation)
        assert actual == expected, (operation, hex(bits), hex(actual), hex(expected))
        count += 1
print(json.dumps({'status': 'PASS_BOUNDED_PLL_ROUNDING_BITS', 'cases': count,
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'limits': 'Raw-word subroutines only; VFP wrapper ABI and PLL caller timing remain separate.'}))
