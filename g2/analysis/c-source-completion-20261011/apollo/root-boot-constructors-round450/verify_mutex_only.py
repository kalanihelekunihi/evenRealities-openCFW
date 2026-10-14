#!/usr/bin/env python3
"""Re-run the stock/source mutex constructor cases after call-path retention."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SPEC = importlib.util.spec_from_file_location('resource_verify', ROOT / 'g2/components/bootloader/thread_creation/verify_resource_creators.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
v = module.v
assert v.sha(v.BLOB) == v.SHA
_, segments, symbols = v.elf.elf_info(args.elf)
fixtures = [('mutex_new', [module.ATTR], dict(cb=cb, size=size, context=context, fail=False, bits=bits))
            for bits, cb, size, context in itertools.product([0, 1, 8, 9, 0x100],
                                                              [0, module.CB], [0, 79, 80], [0, 1])]
fixtures.append(('mutex_new', [0], dict(cb=0, size=0, context=0, fail=False, bits=0)))
for entry, arguments, fixture in fixtures:
    results = []
    for source in (False, True):
        machine = module.Machine(True, segments, symbols) if source else module.Machine()
        machine.context = fixture['context']
        machine.fail_alloc = False
        machine.cpu.mem_write(module.CB, b'\xcc' * 80)
        machine.cpu.mem_write(module.POOL, b'\xcc' * 512)
        for i, value in enumerate([0x433b50, fixture['bits'], fixture['cb'], fixture['size']]):
            machine.w(module.ATTR + i * 4, value)
        machine.cpu.reg_write(v.a.UC_ARM_REG_R7, 0x56789abc)
        returned = machine.run(entry, arguments)['return']
        results.append((returned, machine.events,
                        bytes(machine.cpu.mem_read(module.CB, 80)),
                        bytes(machine.cpu.mem_read(module.POOL, 512))))
    assert results[0] == results[1], (arguments, fixture, results[0][:2], results[1][:2])
result = {'status': 'PASS_BOUNDED_MUTEX_CONSTRUCTOR_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': v.SHA,
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Resource allocator, queue constructors and queue-put remain controlled providers.',
                     'Timer cases are excluded because the existing test fixture compares a callback pointer linked at a different source address; unchanged source fails there too.',
                     'No whole startup, scheduler or hardware behavior is proven.']}
args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], result['cases'])
