#!/usr/bin/env python3
"""Bounded native/source comparison for the three optional startup hook wrappers."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import UC_HOOK_MEM_READ
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[4]
source = ROOT / 'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py'
spec = importlib.util.spec_from_file_location('boot_verify_machine', source)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

CALLBACK = v.STOP + 0x100
HOOKS = [
    ('before', 0x41cd76, 'opencfw_boot_startup_hook_before', 0x20026e4c),
    ('middle', 0x41cd8c, 'opencfw_boot_startup_hook_middle', 0x20026e50),
    ('after', 0x41cda2, 'opencfw_boot_startup_hook_after', 0x20026e54),
]

class Machine(v.Machine):
    def __init__(self, original, segments, symbols):
        super().__init__(not original, segments, symbols)
        self.reads = []
        self.callback_count = 0
        self.cpu.hook_add(UC_HOOK_MEM_READ, self.read)

    def read(self, _uc, _access, address, size, _value, _user):
        if 0x20026e4c <= address <= 0x20026e54:
            self.reads.append([address, size])

    def code(self, uc, pc, size, user):
        if pc == CALLBACK:
            self.callback_count += 1
            uc.reg_write(a.UC_ARM_REG_R0, 37)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        super().code(uc, pc, size, user)

    def call(self, stock_entry, symbol, address, callback):
        self.reads = []
        self.callback_count = 0
        self.done = False
        self.cpu.mem_write(address, struct.pack('<I', CALLBACK | 1 if callback else 0))
        self.cpu.reg_write(a.UC_ARM_REG_XPSR, 0x01000000)
        self.cpu.reg_write(a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, v.STOP | 1)
        self.cpu.reg_write(a.UC_ARM_REG_R0, 0x12345678)
        entry = self.symbols[symbol] & ~1 if self.source else stock_entry
        self.cpu.emu_start(entry | 1, v.STOP + 2, count=10000)
        assert self.done, (self.source, symbol, hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {'result': self.cpu.reg_read(a.UC_ARM_REG_R0),
                'reads': self.reads,
                'callbacks': self.callback_count}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    arg = parser.parse_args()
    assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest() == v.LOCKED_SHA
    _, segments, symbols = v.elf.elf_info(arg.elf)
    cases = []
    native_trace = {}
    for label, native, symbol, address in HOOKS:
        for callback in (False, True):
            pair = [Machine(True, segments, symbols), Machine(False, segments, symbols)]
            observations = [machine.call(native, symbol, address, callback) for machine in pair]
            assert observations[0] == observations[1], (label, callback, observations)
            assert observations[0]['reads'] == [[address, 4]] * (2 if callback else 1)
            assert observations[0]['result'] == (37 if callback else 0)
            assert observations[0]['callbacks'] == int(callback)
            cases.append({'hook': label, 'callback': callback,
                          'observation': observations[0]})
            native_trace.update({hex(pc): value for pc, value in pair[0].trace.items()})
    report = {
        'status': 'PASS_BOUNDED_STARTUP_HOOK_READS',
        'cases': cases,
        'original_sha256': v.LOCKED_SHA,
        'source_elf_sha256': hashlib.sha256(arg.elf.read_bytes()).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'original_trace': native_trace,
        'limits': [
            'Three wrapper entries and zero/nonzero hook words execute in stock and selected source.',
            'A synthetic callback interception returns37; concurrent pointer mutation and physical callback effects are outside this bounded test.',
        ],
    }
    arg.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'cases': len(cases),
                      'source_elf_sha256': report['source_elf_sha256']}))

if __name__ == '__main__':
    main()
