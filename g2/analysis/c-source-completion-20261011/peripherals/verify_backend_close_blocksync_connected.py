#!/usr/bin/env python3
"""Compare native and C close through cache-drop and block-sync state.

Block flush, directory commit, heap-free and fatal-log remain cuts.
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
           for name in ('backend_close.c', 'mlist_isopen.c', 'file_close.c',
                        'mlist_remove.c', 'lfs_free.c')]
SOURCES.extend(ROOT / 'g2/components/audio/file_sync_candidate' / name
               for name in ('file_sync.c', 'file_sync_leaves.c', 'file_flush.c',
                            'bad_block_debug.c', 'cache_drop.c', 'bd_sync.c'))
OBJECTS = [OUT / ('blocksync-connected-' + name.stem + '.o') for name in SOURCES]
ELF = OUT / 'backend-close-blocksync-connected.elf'
for source, obj in zip(SOURCES, OBJECTS):
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)],
                   check=True)
cuts = {'g2_file_close_error': 0x101001,
        'g2_lfs_ctz_tole32': 0x101061,
        'g2_lfs_dir_commit': 0x101071,
        'audio_file_heap_free': 0x101081,
        'g2_lfs_bd_flush': 0x101091,
        'g2_lfs_file_flushedread': 0x1010a1,
        'g2_lfs_file_flushedwrite': 0x1010b1,
        'g2_lfs_file_relocate': 0x1010c1,
        'g2_log_transport_queue_failure': 0x1010d1}
del cuts['g2_lfs_ctz_tole32']
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

def run(native, position, pair_null, bd_result,
        commit_result, has_buffer, flags, flush_result, relocate_result,
        outline_position, sync_result):
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
    write(fs+0x68, 0x20017000)
    write(0x20017010, 0x1010e1)
    write(file+0x30, flags)
    write(file+0x34, outline_position if flags == 0x20000 else 0)
    write(file+0x38, 5)
    write(file+8, 0xffffffff if pair_null else 0)
    write(file+0x28, 0x12345678)
    write(file+0x2c, 4)
    uc.mem_write(file+4, (7).to_bytes(2, 'little'))
    write(cfg, 0x20015000 if has_buffer else 0)
    write(cfg+4, 0x20016000)
    write(cfg+8, 3)
    for reg, value in ((A.UC_ARM_REG_R0, fs), (A.UC_ARM_REG_R1, file),
                       (A.UC_ARM_REG_SP, 0x2007f000),
                       (A.UC_ARM_REG_LR, 0x100f01)):
        uc.reg_write(reg, value)
    original = {0x4d09b4: 'error',
                0x474d16: 'heapfree',
                0x4cd388: 'commit', 0x4caafa: 'bdflush',
                0x4cdd0e: 'relocate', 0x4733ee: 'log',
                0x4ce042: 'read', 0x4ce1a0: 'write'}
    source = {cuts['g2_file_close_error'] & ~1: 'error',
              cuts['audio_file_heap_free'] & ~1: 'heapfree',
              cuts['g2_lfs_dir_commit'] & ~1: 'commit',
              cuts['g2_lfs_bd_flush'] & ~1: 'bdflush',
              cuts['g2_lfs_file_relocate'] & ~1: 'relocate',
              cuts['g2_log_transport_queue_failure'] & ~1: 'log',
              cuts['g2_lfs_file_flushedread'] & ~1: 'read',
              cuts['g2_lfs_file_flushedwrite'] & ~1: 'write'}
    events = []
    done = [False]
    flush_calls = [0]
    def hook(cpu, pc, size, user):
        if pc == 0x100f00:
            done[0] = True
            cpu.emu_stop()
            return
        name = (original if native else source).get(pc)
        if pc == 0x1010e0:
            name = 'sync_fn'
        if name:
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == 'read':
                events.append([name, r3])
                cpu.mem_write(r2, b'X')
            elif name == 'write':
                events.append([name, r3])
                pos = int.from_bytes(cpu.mem_read(file+0x34,4),'little')
                cpu.mem_write(file+0x34, (pos+1).to_bytes(4,'little'))
            elif name == 'log':
                def string(address):
                    raw = bytes(cpu.mem_read(address, 160))
                    return raw.split(b'\0',1)[0].decode('ascii')
                suffix = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),'little')
                events.append([name, string(r0), string(r1), r2, r3, string(suffix)])
            elif name == 'commit':
                raw = cpu.mem_read(r2, 16)
                tags = [int.from_bytes(raw[i:i+4], 'little') for i in (0,8)]
                buffers = [int.from_bytes(raw[i:i+4], 'little') for i in (4,12)]
                buffers = ['stack' if 0x2007e000 <= x < 0x2007f000 else x
                           for x in buffers]
                ctz = cpu.mem_read(int.from_bytes(raw[4:8], 'little'), 8) if \
                    buffers[0] == 'stack' else b''
                events.append([name, r0, r1, tags, buffers, ctz.hex(), r3])
            else:
                normalized_r1 = ('stack' if 0x2007e000 <= r1 < 0x2007f000
                                 else r1)
                events.append([name, r0,
                               normalized_r1 if name != 'heapfree' else None])
            returns = {'commit': commit_result, 'relocate': relocate_result,
                       'read': 1, 'write': 1, 'sync_fn': sync_result}
            if name == 'bdflush':
                if r3 == 0:
                    returns['bdflush'] = bd_result
                else:
                    flush_calls[0] += 1
                    returns['bdflush'] = flush_result if flush_calls[0] == 1 else 0
            cpu.reg_write(A.UC_ARM_REG_R0, returns.get(name, 0))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, hook)
    entry = 0x4cfad0 if native else symbols['audio_file_backend_close']
    uc.emu_start(entry | 1, 0, count=1000)
    assert done[0], (native, position, events)
    return {'result': uc.reg_read(A.UC_ARM_REG_R0), 'events': events,
            'flags': int.from_bytes(uc.mem_read(file+0x30, 4), 'little'),
            'file_words': [int.from_bytes(uc.mem_read(file+off,4),'little')
                           for off in (0x28,0x2c,0x34,0x38)],
            'list_head': int.from_bytes(uc.mem_read(fs+0x28, 4), 'little'),
            'other_next': int.from_bytes(uc.mem_read(other, 4), 'little'),
            'sp': uc.reg_read(A.UC_ARM_REG_SP)}

rows = []
for position in ('missing', 'head', 'second'):
    for flags in (0, 0x80000, 0x10000, 0x110000, 0x40000, 0x120000, 0x20000):
     for pair_null, bd_result, commit_result, sync_result in (
             (0,0,0,0), (1,0,0,0), (0,0xffffffff,0,0),
             (0,0,0xfffffffb,0), (0,0,0,-1), (0,0,0,1)):
      for has_buffer in (False, True):
       for flush_result, relocate_result in ((0,0), (-5,0), (-84,0), (-84,-5)) if flags == 0x20000 else ((0,0),):
        for outline_position in (3,4) if flags == 0x20000 else (0,):
            native = run(True, position, pair_null, bd_result,
                         commit_result, has_buffer, flags, flush_result,
                         relocate_result, outline_position, sync_result)
            source = run(False, position, pair_null, bd_result,
                         commit_result, has_buffer, flags, flush_result,
                         relocate_result, outline_position, sync_result)
            if native != source:
                raise AssertionError((position, pair_null, bd_result,
                                      commit_result, has_buffer, flags,
                                      flush_result, relocate_result,
                                      outline_position, sync_result, native, source))
            names = [event[0] for event in native['events']]
            expected = (['error'] if position == 'missing' else [])
            if not flags & 0x80000:
                if flags == 0x20000:
                    if outline_position == 3:
                        expected.extend(['read','write'])
                    expected.append('bdflush')
                    if flush_result == -84:
                        expected.extend(['log','relocate'])
                        if relocate_result == 0:
                            expected.append('bdflush')
                dirty_after_flush = bool(flags & 0x10000 or flags & 0x20000)
                flush_ok = flush_result == 0 or flush_result == -84 and relocate_result == 0
                if dirty_after_flush and (flags != 0x20000 or flush_ok):
                    if pair_null == 0:
                        if not flags & 0x100000:
                            expected.append('bdflush')
                            if bd_result == 0:
                                expected.append('sync_fn')
                                if sync_result >= 1:
                                    expected.append('error')
                        if flags & 0x100000 or bd_result == 0 and sync_result == 0:
                            expected.append('commit')
            if not has_buffer:
                expected.append('heapfree')
            assert names == expected, (position, flags, has_buffer, names)
            assert native['list_head'] == (0x20012100 if position == 'second' else 0)
            assert native['other_next'] == 0
            rows.append({'position': position, 'pair_null': pair_null, 'bd_result': bd_result,
                         'commit_result': commit_result,
                         'has_buffer': has_buffer, 'flags': flags,
                         'bd_flush_result': flush_result,
                         'relocate_result': relocate_result,
                         'outline_position': outline_position,
                         'sync_result': sync_result})
receipt = {'status': 'PASS_BACKEND_CLOSE_BLOCKSYNC_CONNECTED_BOUNDED', 'cases': len(rows),
           'rows': rows,
           'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in SOURCES},
           'ota_sha256': hashlib.sha256(OTA.read_bytes()).hexdigest(),
           'limits': 'Block-flush, config sync, relocate, dir-commit, heap-free and fatal-log children cut; no actual storage, heap, or fatal-continuation proof.'}
(OUT / 'backend-close-blocksync-connected-results.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(receipt['status'], len(rows))
