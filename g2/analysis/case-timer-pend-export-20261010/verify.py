#!/usr/bin/env python3
"""Compare current Clang timer export with the original producer and queue peers."""
from pathlib import Path
import hashlib
import itertools
import json
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/timer_pend_export.c'
PRIOR = ROOT / 'g2/analysis/case-deferred-event-closure-2026-10-08/verify.py'
CLANG = Path('/usr/bin/clang')
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
OUT = HERE / 'build'
OUT.mkdir(exist_ok=True)
OBJ, ELF, LINK = (OUT / name for name in ('timer_pend_export.o', 'timer_pend_export.elf', 'link.ld'))
LINK.write_text('case_mask_save = 0x080000f5; case_mask_restore = 0x080000fd; case_remove_waiter = 0x0800cba1; case_disinherit = 0x0800cb39; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
compile_cmd = [str(CLANG), '--target=arm-none-eabi', '-mcpu=cortex-m0plus', '-mthumb', '-mfloat-abi=soft', '-std=c11', '-Os', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-c', str(SOURCE), '-o', str(OBJ)]
link_cmd = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-nostdlib', '-T', str(LINK), str(OBJ), '-o', str(ELF)]
subprocess.run(compile_cmd, check=True)
subprocess.run(link_cmd, check=True)
archive_object = ROOT / 'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__timer_pend_export.c.o'
assert hashlib.sha256(OBJ.read_bytes()).digest() == hashlib.sha256(archive_object.read_bytes()).digest()

# Reuse the authenticated image loader, coherent queue fixture, and memory
# comparator; select only the already bounded producer matrix.
prior = PRIOR.read_text()
prefix = prior.split('# Direct copy helper:')[0]
ns = {'__file__': str(PRIOR), '__name__': '__probe__'}
sys.argv = [str(PRIOR), str(ELF)]
exec(compile(prefix, str(PRIOR), 'exec'), ns)
from unicorn.arm_const import UC_ARM_REG_R0
Q, BUF, YIELD, EVENT = (ns[k] for k in ('Q', 'BUF', 'YIELD', 'EVENT'))
states, fixture, execute = (ns[k] for k in ('states', 'fixture', 'execute')) if 'states' in ns else (None, ns['fixture'], ns['execute'])
if states is None:
    def states(length):
        return itertools.product([0, 9, 10], [0, 9]) if length == 10 else itertools.product(range(length + 1), range(length))
rows = []
for length, mask, flags in itertools.product([1, 2, 4, 10], [0, 1], [0, 8, 0x40, 0xffffff]):
    for count, index in states(length):
        vals = []
        for entry in (0x0800ce0c, ns['symbols']['xTimerPendFunctionCallFromISR']):
            u = fixture(length, count, index, 16, -1, mask)
            value = execute(u, entry, [0x0800bf8d, EVENT, flags, YIELD], mask, True)
            copied = bytes(u.mem_read(BUF + index * 16, 16))
            u.mem_write(0x20007000, b'\xee' * 0x1000)
            assert bytes(u.mem_read(BUF + index * 16, 16)) == copied
            if count < length:
                assert copied == struct.pack('<iIII', -2, 0x0800bf8d, EVENT, flags)
            vals.append(value)
        assert vals[0][:2] == vals[1][:2], (length, count, index, mask, flags)
        rows.append({'length': length, 'count': count, 'index': index, 'primask': mask, 'flags': flags})
result = {'status': 'PASS', 'cases': len(rows), 'comparisons': rows,
          'firmware_sha256': hashlib.sha256(ns['ns']['blob']).hexdigest(),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'archive_object_sha256': hashlib.sha256(archive_object.read_bytes()).hexdigest(),
          'compiler_sha256': hashlib.sha256(CLANG.read_bytes()).hexdigest(),
          'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'compile_command': compile_cmd, 'link_command': link_cmd,
          'scope': 'Current Clang producer with original mask and coherent queue peers; no daemon execution.'}
(HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS', len(rows), 'current producer comparisons')
