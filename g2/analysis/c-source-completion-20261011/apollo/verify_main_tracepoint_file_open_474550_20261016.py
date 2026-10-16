#!/usr/bin/env python3
"""Compare the tracepoint file-open caller alias with stock Main's file facade."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_file_open_474550.c'
PROVIDER = G2 / 'components/audio/uart_thread_source_candidate/display_file_api.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-file-open-474550'
OUT.mkdir(parents=True, exist_ok=True)
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
native = {'alloc': 0x474cd2, 'free': 0x474d16, 'acquire': 0x4497b6,
          'release': 0x44981c, 'open': 0x4cfa94}
source = {'alloc': 'codec_allocate', 'free': 'audio_file_heap_free',
          'acquire': 'audio_file_mutex_acquire', 'release': 'audio_file_mutex_release',
          'open': 'audio_file_lfs_open'}
with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    shim = p / 'shim.c'
    elf = p / 'test.elf'
    shim.write_text('''#include <stdint.h>
uint8_t audio_file_lfs_context[4]; void *audio_file_api_mutex;
void *codec_allocate(uint32_t n){(void)n;return 0;}
void audio_file_heap_free(void *p){(void)p;}
int32_t audio_file_mutex_acquire(void *p,uint32_t t){(void)p;(void)t;return 0;}
int32_t audio_file_mutex_release(void *p){(void)p;return 0;}
int32_t audio_file_lfs_open(void *c,void *f,const char *p,uint32_t flags){
 (void)c;(void)f;(void)p;(void)flags;return 0;}
int32_t audio_file_lfs_read(void *a,void *b,void *c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_lfs_seek(void *a,void *b,int32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_lfs_tell(void *a,void *b){(void)a;(void)b;return 0;}
''')
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_tracepoint_file_open_474550',
                    str(SOURCE), str(PROVIDER), str(shim), '-o', str(elf)], check=True)
    syms = {v[2]: int(v[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(v := line.split()) == 3}
    with elf.open('rb') as f:
        segs = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                if s['p_type'] == 'PT_LOAD']

    def run(compiled, path, mode, alloc, acquire, open_result):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segs:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        path_at, mode_at = 0x2007e000, 0x2007e080
        u.mem_write(path_at, path.encode() + b'\0')
        u.mem_write(mode_at, mode.encode() + b'\0')
        hooks = {(syms[source[k]] & ~1 if compiled else address): k
                 for k, address in native.items()}
        calls = []
        def hook(cpu, pc, size, data):
            kind = hooks.get(pc)
            if kind is None:
                return
            r0, r1, r2, r3 = (cpu.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if kind == 'alloc':
                calls.append(('alloc', r0))
                value = 0x20070000 if alloc else 0
            elif kind == 'acquire':
                calls.append(('acquire', r1))
                value = acquire
            elif kind == 'open':
                calls.append(('open', r1, r2, r3))
                value = open_result
            elif kind == 'release':
                calls.append(('release',))
                value = 0
            else:
                calls.append(('free', r0))
                value = 0
            cpu.reg_write(A.UC_ARM_REG_R0, value & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, path_at)
        u.reg_write(A.UC_ARM_REG_R1, mode_at)
        entry = syms['audio_tracepoint_file_open_474550'] if compiled else 0x474550
        u.emu_start(entry | 1, 0x600000, count=3000)
        return u.reg_read(A.UC_ARM_REG_R0), calls

    cases = []
    for path in ('/log/tp/state.bin', '/log/tp/tp_17.bin'):
        for mode in ('rb', 'wb', 'ab', 'rb+', 'w+', 'x'):
            for alloc, acquire, opened in ((False, 0, 0), (True, 1, 0),
                                            (True, 0, -5), (True, 0, 0)):
                n = run(False, path, mode, alloc, acquire, opened)
                c = run(True, path, mode, alloc, acquire, opened)
                if n != c:
                    raise AssertionError((path, mode, alloc, acquire, opened, n, c))
                cases.append((path, mode, alloc, acquire, opened))
    row = {'status': 'PASS_BOUNDED_MAIN_TRACEPOINT_FILE_OPEN_NATIVE_C',
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'provider': str(PROVIDER.relative_to(ROOT)),
           'provider_sha256': hashlib.sha256(PROVIDER.read_bytes()).hexdigest(),
           'payload_sha256': PINNED, 'native_c_cases': len(cases),
           'scope': 'file-open facade allocation, mode flags, mutex, LittleFS, failure and success paths'}
    receipt = OUT / 'oracle.json'
    receipt.write_text(json.dumps(row, indent=2) + '\n')
    print(row['status'], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())
