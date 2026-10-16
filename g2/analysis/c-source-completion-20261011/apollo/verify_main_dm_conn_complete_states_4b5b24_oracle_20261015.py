#!/usr/bin/env python3
"""Compare Cordio special-state CCB lookup with pinned Apollo Main."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_complete_states_4b5b24.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-complete-states-4b5b24'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_dm_connection_records[0xc4];
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
    start = upstream.index('static dmConnCcb_t *dmConnCmplStates(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('DM_CONN_MAX', 'DM_CONN_SM_ST_ACCEPTING',
                 'DM_CONN_SM_ST_DISCONNECTING', 'DM_CONN_HCI_HANDLE_NONE',
                 'DM_TRACE_INFO1'):
        if term not in body:
            raise RuntimeError('Cordio special-state lookup changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_complete_states_4b5b24',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, match_row, mode, vendor, flags, conn_id):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x80000)
            base = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            rows = bytearray((0xa5,) * 0xc4)
            for i in range(3):
                off = i * 0x30
                rows[off + 0x16] = 1
                rows[off + 0x15] = 3
                rows[off + 0x0c:off + 0x0e] = b'\x34\x12'
                rows[off + 0x10] = (conn_id + i) & 0xff
            if match_row >= 0:
                off = match_row * 0x30
                if mode == 'accept':
                    rows[off + 0x15] = 2
                elif mode == 'disconnect':
                    rows[off + 0x15] = 4
                    rows[off + 0x0c:off + 0x0e] = b'\xff\xff'
                elif mode == 'unused':
                    rows[off + 0x15] = 2
                    rows[off + 0x16] = 0
                else:
                    rows[off + 0x15] = 4
            cpu.mem_write(base, bytes(rows))
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
                    calls.append(('wsf', string(uc.reg_read(A.UC_ARM_REG_R0)),
                                  string(uc.reg_read(A.UC_ARM_REG_R1)),
                                  uc.reg_read(A.UC_ARM_REG_R2) & 0xff))
                else:
                    calls.append(('extended', uc.reg_read(A.UC_ARM_REG_R0) & 0xff,
                                  string(uc.reg_read(A.UC_ARM_REG_R1)),
                                  string(uc.reg_read(A.UC_ARM_REG_R2)),
                                  string(uc.reg_read(A.UC_ARM_REG_R3)),
                                  int.from_bytes(uc.mem_read(sp, 4), 'little'),
                                  string(int.from_bytes(uc.mem_read(sp + 4, 4), 'little')),
                                  int.from_bytes(uc.mem_read(sp + 8, 4), 'little') & 0xff))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2007ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_complete_states_4b5b24'] if compiled else 0x4b5b24
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            result = cpu.reg_read(A.UC_ARM_REG_R0)
            return calls, None if result == 0 else result - base, bytes(cpu.mem_read(base, 0xc4))

        cases = 0
        for match_row in (-1, 0, 1, 2):
            for mode in ('accept', 'disconnect', 'unused', 'wrong-handle'):
                for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                    for conn_id in (0, 0x7f):
                        stock = run(False, match_row, mode, vendor, flags, conn_id)
                        candidate = run(True, match_row, mode, vendor, flags, conn_id)
                        if stock != candidate:
                            raise RuntimeError(f'{match_row=} {mode=} {vendor=} {flags=} {conn_id=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_COMPLETE_STATES_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native first-match CCB offset, INFO trace calls and preserved 0xc4-byte DM block.',
               'limits': ['Logger calls are intercepted; actual output and later connection lifecycle remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
