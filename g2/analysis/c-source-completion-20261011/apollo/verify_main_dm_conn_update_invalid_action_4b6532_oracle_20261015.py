#!/usr/bin/env python3
"""Compare Apollo invalid DM action diagnostic calls with compiled C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_update_invalid_action_4b6532.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-update-invalid-action-4b6532'
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
    if blob[0x78eff0 - 0x438000:0x78eff8 - 0x438000] != bytes.fromhex('10 20 11 21 f9 2d 4b 00'):
        raise RuntimeError('DM action table adjacency changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_update_invalid_action',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, vendor, flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            cpu.mem_write(0x20081000, bytes((0, 0, event, 0)) + bytes(20))
            cpu.mem_write(0x20082000, bytes(64))
            cpu.mem_write(0x20073fd8, bytes(12))
            calls = []
            def string(addr):
                data = cpu.mem_read(addr, 200)
                return bytes(data).split(b'\0', 1)[0].decode('ascii', 'replace')
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
                    if 'Invalid action set ID' in fmt:
                        calls.append(('wsf', string(uc.reg_read(A.UC_ARM_REG_R0)), fmt,
                                      uc.reg_read(A.UC_ARM_REG_R2) & 0xff))
                else:
                    fmt_addr = int.from_bytes(uc.mem_read(sp + 4, 4), 'little')
                    fmt = string(fmt_addr)
                    if 'Invalid action set ID' in fmt:
                        value = int.from_bytes(uc.mem_read(sp + 8, 4), 'little')
                        calls.append(('extended', uc.reg_read(A.UC_ARM_REG_R0) & 0xff,
                                      string(uc.reg_read(A.UC_ARM_REG_R1)),
                                      string(uc.reg_read(A.UC_ARM_REG_R2)),
                                      string(uc.reg_read(A.UC_ARM_REG_R3)),
                                      int.from_bytes(uc.mem_read(sp, 4), 'little'),
                                      fmt, value & 0xff))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            if compiled:
                cpu.reg_write(A.UC_ARM_REG_R0, blob[0x78eff0 - 0x438000 + (event & 7)] >> 4)
                entry = symbols['audio_ble_dm_conn_update_invalid_action']
            else:
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20082000)
                cpu.reg_write(A.UC_ARM_REG_R1, 0x20081000)
                entry = 0x4b6532
            cpu.emu_start(entry | 1, 0x600000, count=50000)
            return calls

        cases = 0
        for event in range(256):
            if (event & 7) not in (4, 6):
                continue
            for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                stock = run(False, event, vendor, flags)
                candidate = run(True, event, vendor, flags)
                if stock != candidate:
                    raise RuntimeError(f'event={event} vendor={vendor} flags={flags}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_INVALID_ACTION_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native invalid action-set diagnostics for event indices 4 and 6, vendor logging disabled/enabled, with and without extended log flag.',
               'limits': ['Only the controlled invalid-set diagnostic branch is compared; connection-update actions, actual logger output and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
