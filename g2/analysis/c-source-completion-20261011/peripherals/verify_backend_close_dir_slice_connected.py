#!/usr/bin/env python3
"""Compare native and C close through a valid LittleFS directory slice.

CTZ lookup, file program, device callbacks, directory commit, heap-free and fatal-log remain cuts.
The first metadata pair and one orphan entry execute through traversal over synthetic metadata.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_INVALID
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCES = [ROOT / 'g2/components/audio/file_backend_close_candidate' / name
           for name in ('backend_close.c', 'mlist_isopen.c', 'file_close.c',
                        'mlist_remove.c', 'lfs_free.c')]
SOURCES.extend(ROOT / 'g2/components/audio/file_sync_candidate' / name
               for name in ('file_sync.c', 'file_sync_leaves.c', 'file_flush.c',
                            'bad_block_debug.c', 'cache_drop.c', 'bd_sync.c',
                            'bd_flush.c', 'bd_flush_leaves.c', 'cache_fill.c',
                            'bd_cmp.c', 'byte_compare.c', 'bd_read.c',
                            'byte_copy.c', 'file_flushedread.c',
                            'file_flushedwrite.c', 'alloc_checkpoint.c',
                            'bd_program.c', 'ctz_index.c', 'ctz_find.c',
                            'file_relocate.c', 'bd_erase.c', 'alloc.c',
                            'alloc_scan.c', 'no_space_log.c', 'fs_traverse.c',
                            'tortoise_detectcycles.c', 'dir_fetch.c',
                            'dir_getslice.c', 'gstate_hasmovehere.c'))
OBJECTS = [OUT / ('dir-slice-connected-' + name.stem + '.o') for name in SOURCES]
ELF = OUT / 'backend-close-dir-slice-connected.elf'
for source, obj in zip(SOURCES, OBJECTS):
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)],
                   check=True)
cuts = {'g2_file_close_error': 0x110001,
        'g2_lfs_ctz_tole32': 0x110061,
        'g2_lfs_dir_commit': 0x110071,
        'audio_file_heap_free': 0x110081,
        'g2_log_transport_queue_failure': 0x1100d1,
        'g2_lfs_dir_getread': 0x110141,
        'g2_lfs_file_outline': 0x110171,
        'g2_lfs_ctz_extend': 0x110191,
        'g2_lfs_ctz_traverse': 0x110231,
        }
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
assert max(base+len(data) for base,data in segments) < 0x110000
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob = OTA.read_bytes()[0x20:]

def crc32(crc, data):
    tab = (0,0x1db71064,0x3b6e20c8,0x26d930ac,0x76dc4190,
           0x6b6b51f4,0x4db26158,0x5005713c,0xedb88320,
           0xf00f9344,0xd6d6a3e8,0xcb61b38c,0x9b64c2b0,
           0x86d3d2d4,0xa00ae278,0xbdbdf21c)
    for byte in data:
        crc=(crc>>4)^tab[(crc^byte)&15]
        crc=(crc>>4)^tab[(crc^(byte>>4))&15]
    return crc

disk = [bytearray(b'\xff'*256) for _ in range(2)]
disk[0][0:4]=(1).to_bytes(4,'little')
disk[1][0:4]=(0).to_bytes(4,'little')
tag1=0x00000004
raw1=(tag1^0xffffffff).to_bytes(4,'big')
disk[0][4:8]=raw1
disk[0][8:12]=b'file'
tag2=0x20000008
raw2=(tag2^tag1).to_bytes(4,'big')
disk[0][12:16]=raw2
disk[0][16:24]=(3).to_bytes(4,'little')+(4).to_bytes(4,'little')
tag3=0x500ffc04
raw3=(tag3^tag2).to_bytes(4,'big')
disk[0][24:28]=raw3
checksum=0xffffffff
for part in (disk[0][0:4],raw1,disk[0][8:12],raw2,disk[0][16:24],raw3):
    checksum=crc32(checksum,part)
disk[0][28:32]=checksum.to_bytes(4,'little')

def run(native, position, pair_null, bd_result,
        commit_result, has_buffer, flags, flush_result, relocate_result,
        outline_position, sync_result, read_mismatch, write_result,
        erase_result, alloc_mode):
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
    write(0x20017010, 0x1100e1)
    write(0x20017008, 0x110111)
    write(0x2001700c, 0x1101a1)
    write(0x20017004, 0x110121)
    write(0x20017014, 8)
    write(0x20017018, 16)
    write(0x2001701c, 256)
    write(0x20017028, 16)
    write(0x2001702c, 2)
    write(fs+0x6c, 100)
    write(fs+0x54, 7)
    write(fs+0x58, 0 if alloc_mode.startswith('scan') else 1)
    write(fs+0x5c, 0)
    write(fs+0x60, 16 if alloc_mode == 'scan_full' else 100)
    write(fs+0x64, 0x2001a000)
    uc.mem_write(0x2001a000,b'\0')
    write(fs, 0xffffffff)
    write(fs+4, 0)
    write(fs+8, 0)
    write(fs+12, 0x20019000)
    for cache, block, buffer in ((fs+0x10, 6, 0x20018000),
                                 (file+0x40, 5, 0x20014000)):
        for off, value in ((0,block),(4,0),(8,9),(12,buffer)):
            write(cache+off, value)
    uc.mem_write(0x20014000, b'\xff'*16)
    write(file+0x30, flags)
    write(file+0x34, outline_position if flags == 0x20000 else 0)
    write(file+0x38, 5)
    write(file+8, 0xffffffff if pair_null else 0)
    write(file+0x28, 5)
    write(file+0x2c, 4)
    uc.mem_write(file+4, (7).to_bytes(2, 'little'))
    write(cfg, 0x20015000 if has_buffer else 0)
    write(cfg+4, 0x20016000)
    write(cfg+8, 3)
    for reg, value in ((A.UC_ARM_REG_R0, fs), (A.UC_ARM_REG_R1, file),
                       (A.UC_ARM_REG_SP, 0x2007f000),
                       (A.UC_ARM_REG_LR, 0x110f01)):
        uc.reg_write(reg, value)
    original = {0x4d09b4: 'error',
                0x474d16: 'heapfree',
                0x4cd388: 'commit',
                0x4cf284: 'traverse',
                0x4cef18: 'cycle',
                0x4cbedc: 'fetch',
                0x4cb23a: 'slice',
                0x4caf5c: 'state',
                0x4733ee: 'log',
                }
    source = {cuts['g2_file_close_error'] & ~1: 'error',
              cuts['audio_file_heap_free'] & ~1: 'heapfree',
              cuts['g2_lfs_dir_commit'] & ~1: 'commit',
              symbols['g2_lfs_fs_traverse'] & ~1: 'traverse',
              symbols['g2_lfs_tortoise_detectcycles'] & ~1: 'cycle',
              symbols['g2_lfs_dir_fetch'] & ~1: 'fetch',
              symbols['g2_lfs_dir_getslice'] & ~1: 'slice',
              symbols['g2_lfs_gstate_hasmovehere'] & ~1: 'state',
              cuts['g2_log_transport_queue_failure'] & ~1: 'log',
              cuts['g2_lfs_dir_getread'] & ~1: 'dirread',
              cuts['g2_lfs_file_outline'] & ~1: 'outline',
              cuts['g2_lfs_ctz_extend'] & ~1: 'extend'}
    events = []
    done = [False]
    flush_calls = [0]
    compare_started = [False]
    compare_reads = [0]
    current_validate = [None]
    callback_target = [None]
    traverse_return = [None]
    visit_context = [None]
    visit_blocks = [list(range(7,23)) if alloc_mode == 'scan_full' else [7]]
    visit_index = [0]
    traverse_active = [False]
    def hook(cpu, pc, size, user):
        if pc == 0x110f00:
            done[0] = True
            cpu.emu_stop()
            return
        if pc == 0x1101d0:
            visit_index[0] += 1
            if visit_index[0] < len(visit_blocks[0]):
                cpu.reg_write(A.UC_ARM_REG_R0, visit_context[0])
                cpu.reg_write(A.UC_ARM_REG_R1, visit_blocks[0][visit_index[0]])
                cpu.reg_write(A.UC_ARM_REG_LR, 0x1101d1)
                cpu.reg_write(A.UC_ARM_REG_PC, callback_target[0] | 1)
            else:
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
                cpu.reg_write(A.UC_ARM_REG_PC, traverse_return[0])
            return
        if callback_target[0] is not None and pc == callback_target[0]:
            events.append(['visit',cpu.reg_read(A.UC_ARM_REG_R0),
                           cpu.reg_read(A.UC_ARM_REG_R1)])
        if pc == (0x4caafa if native else symbols['g2_lfs_bd_flush'] & ~1):
            current_validate[0] = cpu.reg_read(A.UC_ARM_REG_R3) & 0xff
        if pc == (0x4caa04 if native else symbols['g2_lfs_bd_cmp'] & ~1):
            compare_started[0] = True
        name = (original if native else source).get(pc)
        if pc == 0x1100e0:
            name = 'sync_fn'
        if pc == 0x110110:
            name = 'prog'
        if pc == 0x110120:
            name = 'read_cb'
        if pc == 0x1101a0:
            name = 'erase_cb'
        if name:
            if name == 'erase_cb':
                traverse_active[0] = False
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == 'erase_cb':
                events.append([name,r0,r1])
            elif name == 'traverse':
                events.append([name,r0,r2,r3])
                callback_target[0] = r1 & ~1
                if alloc_mode in ('scan_used','scan_full'):
                    traverse_return[0] = cpu.reg_read(A.UC_ARM_REG_LR)
                    visit_context[0] = r2
                    visit_index[0] = 0
                    cpu.reg_write(A.UC_ARM_REG_R0, r2)
                    cpu.reg_write(A.UC_ARM_REG_R1, visit_blocks[0][0])
                    cpu.reg_write(A.UC_ARM_REG_LR, 0x1101d1)
                    cpu.reg_write(A.UC_ARM_REG_PC, r1)
                    return
                traverse_active[0] = True
                # Execute first metadata pair with matched cycle/fetch cuts.
                return
            elif name == 'cycle':
                events.append([name])
                return
            elif name == 'fetch':
                events.append([name])
                return
            elif name == 'slice':
                events.append([name, r2, r3])
                return
            elif name == 'state':
                events.append([name])
                return
            elif name == 'log':
                def string(address):
                    try:
                        raw = bytes(cpu.mem_read(address, 160))
                    except Exception as exc:
                        raise AssertionError(('bad-log-string', native, position,
                                              flags, alloc_mode, hex(address),
                                              events[-8:])) from exc
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
            elif name == 'prog':
                length = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),'little')
                events.append([name, r0, r1, r2, r3, length,
                               bytes(cpu.mem_read(r3,length)).hex(),
                               current_validate[0]])
            elif name == 'read_cb':
                length = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),'little')
                normalized_dest = ('stack' if 0x2007e000 <= r3 < 0x2007f000 else r3)
                events.append([name, r0, r1, r2, normalized_dest, length])
                payload = bytearray(cpu.mem_read(0x20014000,length)) if compare_started[0] else bytearray(length)
                if traverse_active[0] and r1 < len(disk) and r2+length <= 256:
                    payload = disk[r1][r2:r2+length]
                if compare_started[0]:
                    compare_reads[0] += 1
                if read_mismatch and compare_reads[0] == 1 and compare_started[0]:
                    payload[0] = 1
                cpu.mem_write(r3, bytes(payload))
            else:
                normalized_r1 = ('stack' if 0x2007e000 <= r1 < 0x2007f000
                                 else r1)
                events.append([name, r0,
                               normalized_r1 if name != 'heapfree' else None])
            returns = {'commit': commit_result,
                       'erase_cb': erase_result,
                       'sync_fn': sync_result,
                       'read_cb': 0}
            if name == 'prog':
                if current_validate[0] == 0:
                    returns['prog'] = bd_result
                else:
                    flush_calls[0] += 1
                    returns['prog'] = flush_result if flush_calls[0] == 1 else 0
            cpu.reg_write(A.UC_ARM_REG_R0, returns.get(name, 0))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, hook)
    def invalid(cpu, access, address, size, value, user):
        print('invalid-memory', native, hex(cpu.reg_read(A.UC_ARM_REG_PC)),
              hex(address), access, size, position, flags,
              flush_result, relocate_result,
              'events',events[-8:],
              'file_buf',bytes(cpu.mem_read(file+0x4c,4)).hex(),
              'fs_buf',bytes(cpu.mem_read(fs+0x1c,4)).hex(),flush=True)
        return False
    uc.hook_add(UC_HOOK_MEM_INVALID, invalid)
    entry = 0x4cfad0 if native else symbols['audio_file_backend_close']
    uc.emu_start(entry | 1, 0, count=8000)
    assert done[0], (native, position, events)
    return {'result': uc.reg_read(A.UC_ARM_REG_R0), 'events': events,
            'flags': int.from_bytes(uc.mem_read(file+0x30, 4), 'little'),
            'file_words': [int.from_bytes(uc.mem_read(file+off,4),'little')
                           for off in (0x28,0x2c,0x34,0x38)],
            'list_head': int.from_bytes(uc.mem_read(fs+0x28, 4), 'little'),
            'other_next': int.from_bytes(uc.mem_read(other, 4), 'little'),
            'program_cache': bytes(uc.mem_read(fs+0x10,16)).hex(),
            'file_cache': bytes(uc.mem_read(file+0x40,16)).hex(),
            'program_buffer': bytes(uc.mem_read(0x20018000,16)).hex(),
            'file_buffer': bytes(uc.mem_read(0x20014000,16)).hex(),
            'read_cache': bytes(uc.mem_read(fs,16)).hex(),
            'read_buffer': bytes(uc.mem_read(0x20019000,16)).hex(),
            'allocator_checkpoint': int.from_bytes(uc.mem_read(fs+0x60,4),'little'),
            'allocator_state': [int.from_bytes(uc.mem_read(fs+off,4),'little')
                                for off in (0x54,0x58,0x5c,0x60,0x64)],
            'lookahead': bytes(uc.mem_read(0x2001a000,2)).hex(),
            'sp': uc.reg_read(A.UC_ARM_REG_SP)}

rows = []
for position in ('missing', 'head', 'second'):
    for flags in (0, 0x80000, 0x10000, 0x110000, 0x40000, 0x120000, 0x20000):
     for pair_null, bd_result, commit_result, sync_result in (
             (0,0,0,0), (1,0,0,0), (0,0xffffffff,0,0),
             (0,0,0xfffffffb,0), (0,0,0,-1), (0,0,0,1)):
      for has_buffer in (False, True):
       for flush_result, relocate_result, read_mismatch, erase_result in (
               ((0,0,False,0), (0,0,True,0), (0,0,True,-5),
                (-5,0,False,0), (-84,0,False,0),
                (-84,0,False,-5)) if flags == 0x20000
               else ((0,0,False,0),)):
        for outline_position, write_result, alloc_mode in (
                ((3,0,'ready'),(3,0,'scan'),(3,0,'scan_used'),
                 (4,0,'ready'),(4,0,'scan'),(4,0,'scan_used'))
                if flags == 0x20000 else ((0,0,'ready'),)):
            native = run(True, position, pair_null, bd_result,
                         commit_result, has_buffer, flags, flush_result,
                         relocate_result, outline_position, sync_result,
                         read_mismatch, write_result, erase_result, alloc_mode)
            source = run(False, position, pair_null, bd_result,
                         commit_result, has_buffer, flags, flush_result,
                         relocate_result, outline_position, sync_result,
                         read_mismatch, write_result, erase_result, alloc_mode)
            if native != source:
                raise AssertionError((position, pair_null, bd_result,
                                      commit_result, has_buffer, flags,
                                      flush_result, relocate_result,
                                      outline_position, sync_result,
                                      read_mismatch, write_result,
                                      erase_result, alloc_mode, native, source))
            if (flags == 0x20000 and write_result == 0 and
                    (flush_result == -84 or read_mismatch) and
                    alloc_mode.startswith('scan')):
                erase_blocks = [event[2] for event in native['events']
                                if event[0] == 'erase_cb']
                assert erase_blocks == [8 if alloc_mode == 'scan_used' else 7]
                assert native['lookahead'].startswith(
                    '01' if alloc_mode == 'scan_used' else '00')
            names = [event[0] for event in native['events']]
            expected = (['error'] if position == 'missing' else [])
            if not flags & 0x80000:
                if flags == 0x20000:
                    if outline_position == 3:
                        expected.append('read_cb')
                    if write_result == 0:
                        expected.append('prog')
                    if flush_result == 0 and write_result == 0:
                        expected.append('read_cb')
                    if write_result == 0 and (flush_result == -84 or read_mismatch):
                        expected.append('log')
                        if alloc_mode.startswith('scan'):
                            expected.append('traverse')
                            if alloc_mode == 'scan_used':
                                expected.append('visit')
                            elif alloc_mode == 'scan':
                                expected.extend(['cycle','visit','visit','fetch',
                                                 'read_cb','read_cb','read_cb',
                                                 'read_cb','read_cb','state',
                                                 'slice','state','read_cb',
                                                 'read_cb','read_cb','visit','visit'])
                        expected.append('erase_cb')
                        if erase_result == 0:
                            if outline_position == 3:
                                expected.append('error')
                            expected.extend(['prog','read_cb'])
                dirty_after_flush = bool(flags & 0x10000 or flags & 0x20000)
                flush_ok = write_result == 0 and (
                    (flush_result == 0 and not read_mismatch) or
                    (flush_result == -84 or read_mismatch) and
                    relocate_result == 0 and erase_result == 0)
                relocated = (flags == 0x20000 and write_result == 0 and
                             (flush_result == -84 or read_mismatch) and
                             relocate_result == 0 and erase_result == 0)
                if dirty_after_flush and (flags != 0x20000 or flush_ok):
                    if pair_null == 0:
                        if not flags & 0x100000:
                            if not relocated:
                                expected.append('prog')
                            if bd_result == 0 or relocated:
                                expected.append('sync_fn')
                                if sync_result >= 1:
                                    expected.append('error')
                        if flags & 0x100000 or (bd_result == 0 or relocated) and sync_result == 0:
                            expected.append('commit')
            if not has_buffer:
                expected.append('heapfree')
            assert names == expected, (position, flags, has_buffer, names, expected,
                                       flush_result, relocate_result,
                                       read_mismatch, erase_result)
            assert native['list_head'] == (0x20012100 if position == 'second' else 0)
            assert native['other_next'] == 0
            rows.append({'position': position, 'pair_null': pair_null, 'bd_result': bd_result,
                         'commit_result': commit_result,
                         'has_buffer': has_buffer, 'flags': flags,
                         'bd_flush_result': flush_result,
                         'relocate_result': relocate_result,
                         'outline_position': outline_position,
                         'sync_result': sync_result,
                         'read_mismatch': read_mismatch,
                         'write_result': write_result,
                         'erase_result': erase_result,
                         'alloc_mode': alloc_mode})
full_args = ('missing',0,0,0,False,0x20000,-84,0,4,0,False,0,0,'scan_full')
full_native = run(True,*full_args)
full_source = run(False,*full_args)
assert full_native == full_source, (full_native,full_source)
assert full_native['result'] == 0xffffffe4
assert full_native['lookahead'] == 'ffff'
assert full_native['allocator_checkpoint'] == 0
assert len([event for event in full_native['events'] if event[0] == 'visit']) == 16
assert any(event[0] == 'log' and 'No more free space' in event[1]
           for event in full_native['events'])
assert not any(event[0] == 'erase_cb' for event in full_native['events'])
rows.append({'special':'full-lookahead-no-space','result':full_native['result']})
receipt = {'status': 'PASS_BACKEND_CLOSE_DIR_SLICE_CONNECTED_BOUNDED', 'cases': len(rows),
           'rows': rows,
           'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in SOURCES},
           'ota_sha256': hashlib.sha256(OTA.read_bytes()).hexdigest(),
           'limits': 'Filesystem traversal, cycle detector, directory fetch and slice execute the first metadata-pair and one orphan entry over synthetic valid LittleFS metadata; full-lookahead cases still use synthetic callback delivery. Device erase/program/read callbacks, config sync, dir-commit, heap-free and fatal-log child cut; no actual storage, heap, or fatal-continuation proof.'}
(OUT / 'backend-close-dir-slice-connected-results.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(receipt['status'], len(rows))
