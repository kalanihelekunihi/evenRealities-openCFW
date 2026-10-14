#!/usr/bin/env python3
"""Compare native and C backend-close through list lookup and close worker.

The sync, list-removal, free, and fatal-log children remain explicit cuts.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCES = [ROOT / 'g2/components/audio/file_backend_close_candidate' / name
           for name in ('backend_close.c', 'mlist_isopen.c', 'file_close.c')]
OBJECTS = [OUT / ('connected-' + name.stem + '.o') for name in SOURCES]
ELF = OUT / 'backend-close-connected.elf'
for source, obj in zip(SOURCES, OBJECTS):
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)],
                   check=True)
cuts = {'g2_file_close_error': 0x101001, 'g2_lfs_file_sync': 0x101011,
        'g2_lfs_mlist_remove': 0x101021, 'g2_lfs_free': 0x101031}
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                *[f'--defsym={name}={value:#x}' for name, value in cuts.items()],
                '-o', str(ELF), *map(str, OBJECTS)], check=True)
with ELF.open('rb') as handle:
    elf = ELFFile(handle)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in
               elf.get_section_by_name('.symtab').iter_symbols()}
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob = OTA.read_bytes()[0x20:]

def run(native, position, sync_result, has_buffer):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    for base, size in ((0x438000, (len(blob)+4095)&~4095),
                       (0x100000, 0x20000), (0x20000000, 0x80000)):
        uc.mem_map(base, size)
    if native:
        uc.mem_write(0x438000, blob)
    else:
        for base, data in segments:
            uc.mem_write(base, data)
    fs, file, other, cfg = 0x20010000, 0x20012000, 0x20012100, 0x20013000
    write = lambda address, value: uc.mem_write(address, value.to_bytes(4, 'little'))
    head = 0 if position == 'missing' else file if position == 'head' else other
    write(fs+0x28, head)
    write(other, file if position == 'second' else 0)
    write(file, 0)
    write(file+0x4c, 0x20014000)
    write(file+0x50, cfg)
    write(cfg, 0x20015000 if has_buffer else 0)
    for reg, value in ((A.UC_ARM_REG_R0, fs), (A.UC_ARM_REG_R1, file),
                       (A.UC_ARM_REG_SP, 0x2007f000),
                       (A.UC_ARM_REG_LR, 0x100f01)):
        uc.reg_write(reg, value)
    original = {0x4d09b4: 'error', 0x4cdf74: 'sync',
                0x4cb0a0: 'remove', 0x4ca812: 'free'}
    source = {cuts['g2_file_close_error'] & ~1: 'error',
              cuts['g2_lfs_file_sync'] & ~1: 'sync',
              cuts['g2_lfs_mlist_remove'] & ~1: 'remove',
              cuts['g2_lfs_free'] & ~1: 'free'}
    events = []
    done = [False]
    def hook(cpu, pc, size, user):
        if pc == 0x100f00:
            done[0] = True
            cpu.emu_stop()
            return
        name = (original if native else source).get(pc)
        if name:
            events.append([name, cpu.reg_read(A.UC_ARM_REG_R0),
                           cpu.reg_read(A.UC_ARM_REG_R1) if name != 'free' else None])
            cpu.reg_write(A.UC_ARM_REG_R0, sync_result if name == 'sync' else 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, hook)
    entry = 0x4cfad0 if native else symbols['audio_file_backend_close']
    uc.emu_start(entry | 1, 0, count=1000)
    assert done[0], (native, position, events)
    return {'result': uc.reg_read(A.UC_ARM_REG_R0), 'events': events,
            'sp': uc.reg_read(A.UC_ARM_REG_SP)}

rows = []
for position in ('missing', 'head', 'second'):
    for result in (0, 0xffffffff, 0xfffffffb):
        for has_buffer in (False, True):
            native = run(True, position, result, has_buffer)
            source = run(False, position, result, has_buffer)
            if native != source:
                raise AssertionError((position, result, has_buffer, native, source))
            names = [event[0] for event in native['events']]
            expected = (['error'] if position == 'missing' else []) + ['sync', 'remove']
            if not has_buffer:
                expected.append('free')
            assert names == expected, (position, result, has_buffer, names)
            rows.append({'position': position, 'sync_result': result,
                         'has_buffer': has_buffer})
receipt = {'status': 'PASS_BACKEND_CLOSE_CONNECTED_BOUNDED', 'cases': len(rows),
           'rows': rows,
           'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in SOURCES},
           'ota_sha256': hashlib.sha256(OTA.read_bytes()).hexdigest(),
           'limits': 'Sync, list removal, free and fatal-log children cut; no storage, heap, or fatal-continuation proof.'}
(OUT / 'backend-close-connected-results.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(receipt['status'], len(rows))
