#!/usr/bin/env python3
"""Bounded stock/source Apollo INFO reader public-entry comparison."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'g2/components/audio/source_candidate_20261010/info_space_reader_provider.c'
PINNED = ROOT / 'third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/am_hal_info.c'
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
OUT = Path('/tmp/audio-info-space-reader')
OUT.mkdir(exist_ok=True)
LD = OUT / 'link.ld'
ELF = OUT / 'reader.elf'
LD.write_text('platform_copy_words = 0x48086b; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC), '-mcpu=cortex-m4', '-mthumb', '-O2', '-std=c11',
                '-ffreestanding', '-fno-builtin', '-nostdlib', '-T', str(LD),
                str(SOURCE), '-o', str(ELF)], check=True)
with ELF.open('rb') as f:
    elf = ELFFile(f)
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    code = elf.get_section_by_name('.text').data()
wrapped = OTA.read_bytes()
assert hashlib.sha256(wrapped).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw = wrapped[32:]
decoder_path = ROOT / 'g2/analysis/audio-platform-callbacks-closure-2026-10-08/itcm_record.py'
spec = importlib.util.spec_from_file_location('authenticated_itcm_record', decoder_path)
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
itcm = decoder.decode_itcm(raw)

def run(stock, case):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    uc.mem_map(0, 0x1000)
    uc.mem_write(0x40, itcm)
    uc.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    uc.mem_write(0x438000, raw)
    uc.mem_map(0x100000, 0x1000)
    uc.mem_write(0x100000, code)
    uc.mem_map(0x20000000, 0x80000)
    uc.mem_map(0x40020000, 0x2000)
    uc.mem_map(0x42000000, 0x8000)
    uc.mem_map(0x41fff000, 0x1000)
    data = b''.join(struct.pack('<I', (i * 0x9e3779b9 + 0x1234567) & 0xffffffff)
                    for i in range(0x8000 // 4))
    uc.mem_write(0x42000000, data)
    uc.mem_write(0x41fff000, b'\x6d' * 0x1000)
    uc.mem_write(0x400201bc, struct.pack('<I', case['shadow']))
    uc.mem_write(0x40021008, struct.pack('<I', case['power']))
    uc.mem_write(0x20010000, b'\xa5' * 24)
    uc.reg_write(UC_ARM_REG_R0, case['space'])
    uc.reg_write(UC_ARM_REG_R1, case['offset'])
    uc.reg_write(UC_ARM_REG_R2, case['words'])
    uc.reg_write(UC_ARM_REG_R3, 0 if case['null'] else 0x20010000)
    uc.reg_write(UC_ARM_REG_SP, 0x2007e000)
    uc.reg_write(UC_ARM_REG_LR, 0x100301)
    calls = []
    writes = []
    def hook(cpu, address, _size, _user):
        if address == 0x48086a:
            src, dst, count = [cpu.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
            calls.append([src, dst, count])
            assert ((0x42000000 <= src and src + count * 4 <= 0x42008000) or
                    (0x41fff000 <= src and src + count * 4 <= 0x42000004)), (case, hex(src), count)
            assert dst == 0x20010000 and count <= 4
            if count == 0:
                # ITCM copy's verified source contract is positive count only.
                cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
    def write(_cpu, _access, address, size, value, _user):
        if 0x20010000 <= address < 0x20010018:
            writes.append([address, size, value])
    uc.hook_add(UC_HOOK_CODE, hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write)
    start = 0x4d3ddb if stock else symbols['audio_info_space_read'] | 1
    uc.emu_start(start, 0x100300, count=700)
    return {
        'result': uc.reg_read(UC_ARM_REG_R0),
        'output': bytes(uc.mem_read(0x20010000, 24)).hex(),
        'calls': calls,
        'writes': writes,
        'shadow': struct.unpack('<I', uc.mem_read(0x400201bc, 4))[0],
        'power': struct.unpack('<I', uc.mem_read(0x40021008, 4))[0],
        'sp': uc.reg_read(UC_ARM_REG_SP),
        'pc': uc.reg_read(UC_ARM_REG_PC),
    }

cases = []
for space in range(6):
    for shadow in (0, 0x8, 0x10, 0x18):
        for power in (0, 0x08000000):
            for offset, words in ((0, 1), (31, 2), (511, 1), (512, 1),
                                  (703, 1), (704, 1), (1535, 1), (1536, 1),
                                  (0, 0), (0xffffffff, 2)):
                cases.append(dict(space=space, shadow=shadow, power=power,
                                  offset=offset, words=words, null=False))
for space in (0, 1, 2, 3, 4, 5, 6, 0x101, 0xffffffff):
    cases.append(dict(space=space, shadow=0x18, power=0x08000000,
                      offset=0, words=1, null=True))
    cases.append(dict(space=space, shadow=0x18, power=0x08000000,
                      offset=0, words=1, null=False))
rows = []
for case in cases:
    old = run(True, case)
    new = run(False, case)
    assert old == new, (case, old, new)
    rows.append({'input': case, 'state': old})
receipt = {
    'status': 'PASS', 'fresh_cases': len(rows), 'original_entry': '0x4d3dda',
    'source_entry': hex(symbols['audio_info_space_read'] & ~1),
    'ota_sha256': hashlib.sha256(wrapped).hexdigest(),
    'pinned_source_sha256': hashlib.sha256(PINNED.read_bytes()).hexdigest(),
    'decoded_itcm_sha256': hashlib.sha256(itcm).hexdigest(),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'gcc_sha256': hashlib.sha256(GCC.read_bytes()).hexdigest(),
    'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
    'link_script': LD.read_text(), 'cases': rows,
    'limits': ['Positive-word cases execute the common stock 0x48086a wrapper and authenticated startup-decoded ITCM 0x48 child on both sides; INFO windows and power registers are synthetic mapped memory, not hardware.',
               'Zero-word calls are compared at the reader/child ABI only; the selected copy helper has a positive-count contract.']
}
(HERE / 'info-space-reader-execution.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS', len(rows), 'INFO reader public-entry cases')
