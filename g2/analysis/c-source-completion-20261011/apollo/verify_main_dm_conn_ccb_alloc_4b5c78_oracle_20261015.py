#!/usr/bin/env python3
"""Compare compiled Cordio CCB allocation with pinned Apollo Main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_ccb_alloc_4b5c78.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-ccb-alloc-4b5c78'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_dm_connection_records[0xc4];
__attribute__((noinline)) void audio_uart_buffer_zero(void*a,uint32_t n,uint32_t v){(void)a;(void)n;(void)v;}
__attribute__((noinline)) void audio_ble_copy_address6_4d293c(void*a,const void*b){(void)a;(void)b;}
__attribute__((noinline)) uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
__attribute__((noinline)) int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
__attribute__((noinline)) uint32_t audio_log_flags(void){return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
__attribute__((noinline)) void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('dmConnCcb_t *dmConnCcbAlloc(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('DM_CONN_MAX', 'memset', 'BdaCpy', 'DM_TRACE_ALLOC1', 'DM_TRACE_ERR0'):
        if term not in body:
            raise RuntimeError('Cordio allocation source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_ccb_alloc_4b5c78',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, occupied_mask, vendor, flags, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x80000)
            base = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            rows = bytearray((seed + i * 3) & 0xff for i in range(0xc4))
            for i in range(3):
                rows[i * 0x30 + 0x16] = 1 if occupied_mask & (1 << i) else 0
            address_bytes = bytes(((seed + 0x40 + i) & 0xff for i in range(6)))
            cpu.mem_write(base, bytes(rows))
            cpu.mem_write(0x20002000, address_bytes)
            calls = []
            def string(addr):
                return bytes(cpu.mem_read(addr, 200)).split(b'\0', 1)[0].decode('ascii', 'replace')
            addresses = {
                (symbols['audio_uart_buffer_zero'] & ~1) if compiled else 0x43c0e4: 'zero',
                (symbols['audio_ble_copy_address6_4d293c'] & ~1) if compiled else 0x4d293c: 'copy',
                (symbols['audio_ble_hci_vendor_log_enabled_4c9c50'] & ~1) if compiled else 0x4c9c50: 'vendor',
                (symbols['audio_ble_hci_vendor_compare_44b610'] & ~1) if compiled else 0x44b610: 'compare',
                (symbols['audio_log_flags'] & ~1) if compiled else 0x43d0ce: 'flags',
                (symbols['audio_log_extended'] & ~1) if compiled else 0x43d574: 'extended',
                (symbols['audio_ble_hci_wsf_trace'] & ~1) if compiled else 0x52a63c: 'wsf',
            }
            def hook(uc, location, size, user):
                kind = addresses.get(location)
                if kind is None:
                    return
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                c = uc.reg_read(A.UC_ARM_REG_R2)
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                if kind == 'zero':
                    calls.append(('zero', a - base, b, c))
                    uc.mem_write(a, bytes((c & 0xff,)) * b)
                elif kind == 'copy':
                    data = bytes(uc.mem_read(b, 6))
                    calls.append(('copy', a - base, data))
                    uc.mem_write(a, data)
                elif kind == 'vendor':
                    uc.reg_write(A.UC_ARM_REG_R0, vendor)
                elif kind == 'compare':
                    left = string(a)
                    right = string(b)
                    uc.reg_write(A.UC_ARM_REG_R0, 0 if left[:c] == right[:c] else 1)
                elif kind == 'flags':
                    uc.reg_write(A.UC_ARM_REG_R0, flags)
                elif kind == 'wsf':
                    fmt = string(b)
                    calls.append(('wsf', string(a), fmt,
                                  (c & 0xff) if '%d' in fmt else None))
                else:
                    fmt = string(int.from_bytes(uc.mem_read(sp + 4, 4), 'little'))
                    calls.append(('extended', a & 0xff, string(b), string(c),
                                  string(uc.reg_read(A.UC_ARM_REG_R3)),
                                  int.from_bytes(uc.mem_read(sp, 4), 'little'), fmt,
                                  (int.from_bytes(uc.mem_read(sp + 8, 4), 'little') & 0xff)
                                  if '%d' in fmt else None))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2007ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_ccb_alloc_4b5c78'] if compiled else 0x4b5c78
            cpu.emu_start(entry | 1, 0x600000, count=20000)
            result = cpu.reg_read(A.UC_ARM_REG_R0)
            return calls, None if result == 0 else result - base, bytes(cpu.mem_read(base, 0xc4))

        cases = 0
        for occupied_mask in range(8):
            for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                for seed in (0, 0x55):
                    stock = run(False, occupied_mask, vendor, flags, seed)
                    candidate = run(True, occupied_mask, vendor, flags, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{occupied_mask=} {vendor=} {flags=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_CCB_ALLOC_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native row clearing/address copying, CCB initialization, success/failure trace, and return offset.',
               'limits': ['Fill, copy and logger effects are cut at native call boundaries; final memory placement remains open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
