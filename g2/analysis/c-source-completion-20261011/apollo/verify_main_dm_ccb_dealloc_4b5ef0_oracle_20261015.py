#!/usr/bin/env python3
"""Compare compiled Cordio CCB deallocation with Apollo native effects."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_ccb_dealloc_4b5ef0.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-ccb-dealloc-4b5ef0'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
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
    start = upstream.index('void dmConnCcbDealloc(')
    end = upstream.index('\n}', start)
    if 'DM_TRACE_FREE1' not in upstream[start:end] or 'pCcb->inUse = FALSE' not in upstream[start:end]:
        raise RuntimeError('Cordio CCB deallocator source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_ccb_dealloc_4b5ef0',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, conn_id, in_use, vendor, flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytearray((0xa5,) * 64)
            ccb[0x10] = conn_id
            ccb[0x16] = in_use
            cpu.mem_write(0x20001000, bytes(ccb))
            calls = []
            def string(addr):
                return bytes(cpu.mem_read(addr, 200)).split(b'\0', 1)[0].decode('ascii', 'replace')
            addresses = {
                (symbols['audio_ble_hci_vendor_log_enabled_4c9c50'] & ~1) if compiled else 0x4c9c50: 'vendor',
                (symbols['audio_ble_hci_vendor_compare_44b610'] & ~1) if compiled else 0x44b610: 'compare',
                (symbols['audio_log_flags'] & ~1) if compiled else 0x43d0ce: 'flags',
                (symbols['audio_log_extended'] & ~1) if compiled else 0x43d574: 'extended',
                (symbols['audio_ble_hci_wsf_trace'] & ~1) if compiled else 0x52a63c: 'wsf',
            }
            def hook(uc, address, size, user):
                kind = addresses.get(address)
                if kind is None:
                    return
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                if kind == 'vendor':
                    uc.reg_write(A.UC_ARM_REG_R0, vendor)
                elif kind == 'compare':
                    left = string(uc.reg_read(A.UC_ARM_REG_R0))
                    right = string(uc.reg_read(A.UC_ARM_REG_R1))
                    length = uc.reg_read(A.UC_ARM_REG_R2)
                    uc.reg_write(A.UC_ARM_REG_R0, 0 if left[:length] == right[:length] else 1)
                elif kind == 'flags':
                    uc.reg_write(A.UC_ARM_REG_R0, flags)
                elif kind == 'wsf':
                    fmt = string(uc.reg_read(A.UC_ARM_REG_R1))
                    calls.append(('wsf', string(uc.reg_read(A.UC_ARM_REG_R0)), fmt,
                                  uc.reg_read(A.UC_ARM_REG_R2) & 0xff))
                else:
                    fmt = string(int.from_bytes(uc.mem_read(sp + 4, 4), 'little'))
                    calls.append(('extended', uc.reg_read(A.UC_ARM_REG_R0) & 0xff,
                                  string(uc.reg_read(A.UC_ARM_REG_R1)),
                                  string(uc.reg_read(A.UC_ARM_REG_R2)),
                                  string(uc.reg_read(A.UC_ARM_REG_R3)),
                                  int.from_bytes(uc.mem_read(sp, 4), 'little'),
                                  fmt, int.from_bytes(uc.mem_read(sp + 8, 4), 'little') & 0xff))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_ccb_dealloc_4b5ef0'] if compiled else 0x4b5ef0
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            return calls, bytes(cpu.mem_read(0x20001000, 64))

        cases = 0
        for conn_id in (0, 1, 2, 0x7f, 0xff):
            for in_use in (0, 1, 0xa5):
                for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                    stock = run(False, conn_id, in_use, vendor, flags)
                    candidate = run(True, conn_id, in_use, vendor, flags)
                    if stock != candidate:
                        raise RuntimeError(f'{conn_id=} {in_use=} {vendor=} {flags=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CCB_DEALLOC_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native FREE trace calls and CCB in-use byte mutation across IDs and logger settings.',
               'limits': ['Actual logger output and connection lifecycle after deallocation remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
