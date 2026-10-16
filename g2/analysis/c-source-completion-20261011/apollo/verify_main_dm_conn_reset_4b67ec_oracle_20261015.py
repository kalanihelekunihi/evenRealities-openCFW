#!/usr/bin/env python3
"""Compare C Cordio connection reset with pinned Apollo Main calls and RAM."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_reset_4b67ec.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-reset-4b67ec'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_dm_connection_records[0xc4];
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) void audio_ble_dm_conn_hci_handler_4b68a4(void*a){(void)a;}
__attribute__((noinline)) void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){(void)b;(void)n;return a;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConnReset(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('DM_CONN_MAX', 'dmConnHciHandler', 'DM_NUM_PHYS',
                 'dmConnSpecDefaults', 'dmCb.initFiltPolicy', 'dmCb.connAddrType'):
        if term not in body:
            raise RuntimeError('Cordio reset source changed')
    stock_defaults = blob[0x78a814 - 0x438000:0x78a814 - 0x438000 + 12]
    if stock_defaults != bytes((0x18, 0, 0x28, 0, 0, 0, 0xd0, 7, 0, 0, 0, 0)):
        raise RuntimeError('stock connection defaults changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_reset_4b67ec',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        defaults_address = symbols['audio_ble_dm_conn_spec_defaults_78a814']
        defaults_bytes = next(seg[defaults_address - address:defaults_address - address + 12]
                              for address, seg in segments
                              if address <= defaults_address < address + len(seg))
        if defaults_bytes != stock_defaults:
            raise RuntimeError('compiled connection defaults differ')

        def run(compiled, mask, handle_base, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x80000)
            base = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            state = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            rows = bytearray(((seed + i * 5) & 0xff for i in range(0xc4)))
            for i in range(3):
                rows[i * 0x30 + 0x16] = 1 if mask & (1 << i) else 0
                rows[i * 0x30 + 0x0c:i * 0x30 + 0x0e] = (handle_base + i * 17).to_bytes(2, 'little')
            dm = bytes(((seed + i * 7) & 0xff for i in range(0x18)))
            cpu.mem_write(base, bytes(rows))
            cpu.mem_write(state, dm)
            calls = []
            hci = (symbols['audio_ble_dm_conn_hci_handler_4b68a4'] & ~1) if compiled else 0x4b68a4
            copy = (symbols['audio_queue_copy_bytes'] & ~1) if compiled else 0x439be4
            def hook(uc, addr, size, user):
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                n = uc.reg_read(A.UC_ARM_REG_R2)
                if addr == hci:
                    event = bytes(uc.mem_read(a, 9))
                    calls.append(('hci', tuple(event[i] for i in (0, 1, 2, 3, 4, 6, 7, 8))))
                elif addr == copy:
                    data = bytes(uc.mem_read(b, n))
                    calls.append(('copy', a - base, n, data))
                    uc.mem_write(a, data)
                    uc.reg_write(A.UC_ARM_REG_R0, a)
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2007ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_reset_4b67ec'] if compiled else 0x4b67ec
            cpu.emu_start(entry | 1, 0x600000, count=3000)
            return calls, bytes(cpu.mem_read(base, 0xc4)), bytes(cpu.mem_read(state, 0x18))

        cases = 0
        for mask in range(8):
            for handle_base in (0, 0x1234, 0xff00):
                for seed in (0, 0x55, 0xa5):
                    stock = run(False, mask, handle_base, seed)
                    candidate = run(True, mask, handle_base, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{mask=} {handle_base=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_RESET_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases, 'stock_defaults_hex': stock_defaults.hex(),
               'comparison_scope': 'Native HCI callback event assigned bytes, copy calls, 0xc4-byte DM block and 0x18-byte global state over CCB masks/handles.',
               'limits': ['One uninitialized HCI event stack byte is excluded from equality.',
                          'HCI event handling and copy are cut at native call boundaries; reset and startup behavior remain unqualified.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
