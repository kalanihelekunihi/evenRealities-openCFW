#!/usr/bin/env python3
"""Compare source formatter to fixed CASE entry for bounded simple formats."""
from pathlib import Path
import ast
import hashlib
import random
import re
import struct
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SRC = ROOT / 'g2/components/case/legacy_default_candidate_20261010/vformat_candidate.c'
FW = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
firmware = FW.read_bytes()
assert hashlib.sha256(firmware).hexdigest() == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
obj = HERE / 'vformat_candidate.o'
elf = HERE / 'vformat_candidate.elf'
script = HERE / 'vformat_candidate.ld'
script.write_text('''
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
''')
subprocess.run(['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m0plus',
                '-mthumb', '-std=c11', '-Os', '-ffreestanding', '-fno-builtin',
                '-c', str(SRC), '-o', str(obj)], check=True)
assert not subprocess.run(['/opt/homebrew/bin/arm-none-eabi-nm', '-u', str(obj)],
                          check=True, capture_output=True, text=True).stdout.strip()
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld', '-T', str(script), str(obj),
                '-o', str(elf)], check=True)
with elf.open('rb') as stream:
    e = ELFFile(stream)
    segments = [(s['p_vaddr'], s.data()) for s in e.iter_segments()
                if s['p_type'] == 'PT_LOAD']
    symbol = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

STOP = 0x20001000
CALLBACK = 0x0010f000
FMT = 0x20004000
ARGS = 0x20005000
cases = [(b'', []), (b'plain text', []), (b'%%', []),
         (b'pre %c end', [65]), (b'%5c', [65]), (b'%-5c', [65]),
         (b'%s', [0x20006000]), (b'%.3s', [0x20006000]),
         (b'%8.3s', [0x20006000]), (b'%.0s', [0x20006000]),
         (b'%d', [42]), (b'%u', [42]), (b'%x', [0x1234]),
         (b'%08x', [0x1234]), (b'%#x', [0x1234]), (b'%o', [42]),
         (b'%+d', [42]), (b'% d', [42]), (b'%-8d', [42]),
         (b'%08d', [42]), (b'%.4d', [42]), (b'%8.4d', [42]),
         (b'%*d', [6, 42]), (b'%.*s', [3, 0x20006000]),
         (b'%X', [0x12ab]), (b'%p', [0x20006000]),
         (b'%hhd', [0xff]), (b'%hd', [0xffff]),
         (b'%ld', [42]), (b'%llu', [0x89abcdef, 0x01234567]),
         (b'%llx', [0x89abcdef, 0x01234567]),
         (b'ab%ncd', [0x20007080]), (b'ab%hncd', [0x20007080]),
         (b'ab%hhncd', [0x20007080]),
         (b'%d', [0xffffffff]), (b'%d', [0x80000000]),
         (b'%08d', [0xffffffff]), (b'%#08x', [0]),
         (b'%.0d', [0]), (b'%#.0o', [0]),
         (b'%*d', [0xfffffffa, 42]),
         (b'%.*d', [0xffffffff, 42]),
         (b'%q', [])]
for fmt in (b'%p', b'%#p', b'%#.0p', b'%#012p', b'%-#12p',
            b'%s', b'%10s', b'%010s', b'%.0s', b'%#s'):
    cases.append((fmt, [0]))
for spec in (b'%d', b'%i', b'%u', b'%o', b'%x', b'%X',
             b'%4d', b'%-4d', b'%04d', b'%+d', b'% d',
             b'%.3d', b'%6.3d', b'%#x', b'%#o', b'%p'):
    for value in (0, 1, 7, 10, 255, 0x80000000, 0xffffffff):
        cases.append((spec, [value]))
actual_formats = set()
for source in (ROOT / 'g2/components/case').rglob('*.c'):
    if 'build' in source.parts:
        continue
    body = source.read_text(errors='replace')
    pattern = (r'(?:g2_log_printf|case_[A-Za-z0-9_]*(?:logger|log))\s*\(\s*'
               r'|(?:static\s+)?const\s+char\s+[A-Za-z0-9_]+\s*\[\s*\]\s*=\s*')
    for match in re.finditer(pattern+r'("(?:\\.|[^"\\])*")', body):
        try:
            value = ast.literal_eval(match.group(1)).encode('latin1')
        except (SyntaxError, ValueError, UnicodeEncodeError):
            continue
        if value and len(value) < 160 and b'*' not in value and b'%n' not in value:
            actual_formats.add(value)
for fmt in sorted(actual_formats):
    cases.append((fmt, [0x20006000]*16))
native_caller_formats = set()
retained = (ROOT / 'g2/tools/manifests/g2-box-ghidra-decomp.c').read_text()
payload = firmware[32:]
for match in re.finditer(r'FUN_08009170\(([^,)]+)', retained):
    argument = match.group(1)
    address = re.search(r'0800([0-9a-fA-F]{4})', argument)
    if not address:
        continue
    offset = int(address.group(1), 16) + (1 if '+ 1' in argument else 0)
    if offset >= len(payload):
        continue
    end = payload.find(b'\0', offset, min(len(payload), offset+160))
    if end < 0:
        continue
    value = payload[offset:end]
    if value and all(x in (9, 10, 13) or 32 <= x <= 126 for x in value):
        native_caller_formats.add(value)
for fmt in sorted(native_caller_formats - actual_formats):
    cases.append((fmt, [0x20006000]*16))
rng = random.Random(0x9210)
for _ in range(512):
    conversion = rng.choice('diuoxXcsp')
    flags = ''.join(ch for ch in '-+ #0' if rng.randrange(2))
    width = '' if rng.randrange(3)==0 else str(rng.randrange(0,13))
    precision = '' if rng.randrange(3)==0 else '.'+str(rng.randrange(0,9))
    fmt = ('%' + flags + width + precision + conversion).encode('ascii')
    value = 0x20006000 if conversion in 'sp' else rng.getrandbits(32)
    cases.append((fmt, [value]))
for conversion in (b'd', b'i', b'u', b'o', b'x', b'X'):
    for length in (b'll', b'j'):
        for value in (0, 1, 0xffffffff, 0x100000000,
                      0x7fffffffffffffff, 0x8000000000000000,
                      0xffffffffffffffff):
            words = [value & 0xffffffff, value >> 32]
            cases.append((b'%' + length + conversion, words))
            cases.append((b'%#024.16' + length + conversion, words))
for conversion in (b'd', b'u', b'x', b'X'):
    for length in (b'z', b't', b'L', b'h', b'hh'):
        for value in (0, 1, 0x80000000, 0xffffffff):
            cases.append((b'%' + length + conversion, [value]))
for fmt in (b'%lln', b'%jn', b'%zn', b'%tn', b'%ln'):
    cases.append((b'xy' + fmt + b'z', [0x20007080, 0]))
for fmt, words in cases:
    observations = []
    for original in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
        u.mem_map(0x08000000, (len(firmware[32:])+4095)&~4095)
        u.mem_write(0x08000000, firmware[32:])
        u.mem_map(0x00100000, 0x10000)
        for address, data in segments: u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_write(FMT, fmt+b'\0')
        u.mem_write(ARGS, struct.pack('<'+'I'*len(words), *words) if words else b'\0'*4)
        u.mem_write(0x20006000, b'hello\0')
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR),
                              (FMT, ARGS, 0x20007000, CALLBACK|1,
                               0x2000f000, STOP|1)):
            u.reg_write(reg, value)
        emitted = []
        def hook(uc, address, size, _):
            if address == CALLBACK:
                emitted.append(uc.reg_read(UC_ARM_REG_R0))
                uc.reg_write(UC_ARM_REG_R0, 0x12345678)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        start = 0x08009210 if original else symbol['case_vformat']
        try:
            u.emu_start(start|1, STOP, count=1000000)
        except Exception as exc:
            if words == [0] and b's' in fmt and 'Invalid memory read' in str(exc):
                observations.append(('native_null_string_fault', bytes(emitted)))
                continue
            raise AssertionError((fmt, original, hex(u.reg_read(UC_ARM_REG_PC)), str(exc))) from exc
        assert u.reg_read(UC_ARM_REG_PC) == STOP, (fmt, original, hex(u.reg_read(UC_ARM_REG_PC)), len(emitted))
        observations.append((bytes(x&255 for x in emitted), u.reg_read(UC_ARM_REG_R0),
                             bytes(u.mem_read(0x20007080, 8)) if b'%n' in fmt or b'%hn' in fmt or b'%hhn' in fmt else b''))
    assert observations[0] == observations[1], (fmt, observations)
print('PASS_VFORMAT_BASIC', len(cases), 'actual_source_formats', len(actual_formats),
      'retained_native_caller_formats', len(native_caller_formats))
