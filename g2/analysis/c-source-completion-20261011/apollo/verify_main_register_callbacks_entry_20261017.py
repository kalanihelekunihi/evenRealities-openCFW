#!/usr/bin/env python3
"""Check the C startup registration entry against stock callback-table effects."""
import hashlib
import itertools
import json
import runpy
import struct
from pathlib import Path

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_R0

ROOT = Path(__file__).resolve().parents[4]
LEGACY = ROOT / 'g2/analysis/audio-platform-callbacks-closure-2026-10-08'
HERE = ROOT / 'g2/build/c-firmware/20261017/main-register-callbacks-entry'
SOURCE = ROOT / 'g2/components/audio/platform_callbacks_offline/stock_register_callbacks_entry.c'
BODY = ROOT / 'g2/components/audio/platform_callbacks_offline/callbacks.c'
STOCK_FIRST_CHILDREN = {0x5a4d48, 0x5a1c18, 0x5a08e4, 0x5a0018}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    scope = runpy.run_path(str(LEGACY / 'verify.py'))
    assert 'stock_register_callbacks' in scope['sym']
    machine, w, expected = scope['machine'], scope['w'], scope['expected']
    count = 0
    for major, revision, feature, initial in itertools.product(
            [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0xdead0021],
            [0, 1, 2, 3, 4, 0xffffffff], [0, 1], [0, 0xa5a5a5a5]):
        table, flags = expected(major, revision, feature)
        values = []
        for entry in (0x480434, scope['sym']['stock_register_callbacks']):
            u = machine()
            w(u, 0x4002000c, major)
            w(u, 0x200001e8, revision)
            u.mem_write(0x2007197c, bytes([feature]))
            u.mem_write(0x2007326c, b'\xa5' * 68)
            u.mem_write(0x20074f60, b'\xa5' * 16)
            w(u, 0x40020028, initial)
            w(u, 0x40020060, initial)
            writes, boundary = [], []

            def code_hook(emu, address, size, data):
                if address in STOCK_FIRST_CHILDREN:
                    boundary.append(address)
                    emu.emu_stop()

            def write_hook(emu, access, address, size, value, data):
                writes.append((address, size, value))

            u.hook_add(UC_HOOK_CODE, code_hook)
            u.hook_add(UC_HOOK_MEM_WRITE, write_hook,
                       begin=0x40020028, end=0x40020063)
            u.emu_start(entry | 1, 0x2007f000, count=10000)
            actual_table = list(struct.unpack('<15I', u.mem_read(0x20073270, 60)))
            actual_flags = list(u.mem_read(0x20074f64, 6))
            assert actual_table == table and actual_flags == flags
            assert bytes(u.mem_read(0x2007326c, 4)) == b'\xa5' * 4
            assert bytes(u.mem_read(0x200732ac, 4)) == b'\xa5' * 4
            assert boundary == ([table[0] & ~1] if table[0] else [])
            if not table[0]:
                assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000
                assert u.reg_read(UC_ARM_REG_R0) == 0
            values.append((actual_table, actual_flags, writes, boundary))
        assert values[0] == values[1], (major, revision, feature, initial)
        count += 1
    assert count == 168
    record = {
        'status': 'PASS_MAIN_REGISTER_CALLBACKS_ENTRY_STOCK_MATCH',
        'cases': count,
        'entry_source_sha256': sha(SOURCE), 'body_source_sha256': sha(BODY),
        'native_elf_sha256': sha(scope['elf']),
        'stock_entry': '0x480434',
        'comparison': 'full 15-word table, six feature flags, MMIO write sequence, first child boundary',
        'limits': ['Callback targets still include stock function addresses; full C provider graph is incomplete.',
                   'Revision inputs and MMIO effects are modeled, not measured on hardware.'],
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    output = HERE / 'entry-oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()
