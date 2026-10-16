#!/usr/bin/env python3
"""Compare the pinned Cordio PHY interface and HCI indications to C."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_phy_interface_78a85c.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_phy.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-phy-interface-78a85c'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_empty_reset_4d29be', 0x4d29bf),
         ('audio_ble_dm_phy_hci_handler_4c5734', 0x4c5735),
         ('audio_ble_dm_empty_handler_4d29c0', 0x4d29c1)]
SHIM = '''#include <stdint.h>
uint8_t audio_dm_connection_records[196];
__attribute__((noinline)) void audio_ble_dm_empty_reset_4d29be(void){}
__attribute__((noinline)) void audio_ble_dm_empty_handler_4d29c0(void*x){(void)x;}
__attribute__((noinline)) uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t x){(void)x;return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmPhyHciHandler(hciEvt_t *pEvent)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    stock_table = struct.unpack_from('<III', blob, 0x78a85c - 0x438000)
    if stock_table != tuple(address for _, address in SLOTS):
        raise RuntimeError('native PHY interface changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_phy_hci_handler_4c5734',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def read_elf(address, size):
            for base, data in segments:
                if base <= address and address + size <= base + len(data):
                    return data[address-base:address-base+size]
            raise RuntimeError('table not in load segments')
        table = struct.unpack('<III', read_elf(symbols['audio_ble_dm_phy_table'], 12))
        if table != tuple(symbols[name] for name, _ in SLOTS):
            raise RuntimeError('C PHY interface slots changed')

        def run(compiled, kind, present, status, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            record = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            cpu.mem_write(record + 0x9c, (0x20007001).to_bytes(4, 'little'))
            ccb = bytearray((seed + i * 5) & 0xff for i in range(48))
            ccb[0x0c:0x0e] = (0x1234).to_bytes(2, 'little')
            ccb[0x10] = 3
            cpu.mem_write(0x20003000, bytes(ccb))
            event = bytearray((seed + i * 7) & 0xff for i in range(24))
            event[0:2] = (0x1234).to_bytes(2, 'little')
            event[2] = kind
            event[4] = status
            event[8:10] = b'\x02\x03'
            cpu.mem_write(0x20001000, bytes(event))
            lookup = ((symbols['audio_ble_dm_conn_ccb_by_handle_4b601c'] if compiled
                       else 0x4b601c) & ~1)
            calls = []
            def hook(uc, addr, size, user):
                if addr == lookup:
                    calls.append(('lookup', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20003000 if present else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    data = bytes(uc.mem_read(ptr, 10))
                    calls.append(('callback', data[0:5].hex(), data[6:10].hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_phy_hci_handler_4c5734'] if compiled else 0x4c5734
            cpu.emu_start(entry | 1, 0x600000, count=500)
            return calls

        cases = 0
        for kind in (0x29, 0x2a, 0x2b, 0x2c):
            for present in (False, True):
                for status in (0, 1, 0xff):
                    for seed in (0, 0xa5):
                        stock = run(False, kind, present, status, seed)
                        candidate = run(True, kind, present, status, seed)
                        if stock != candidate:
                            raise RuntimeError(f'{kind=} {present=} {status=} {seed=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PHY_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'native_slots': [hex(x) for x in stock_table],
               'cases': cases,
               'comparison_scope': 'Three PHY table pointers and bounded native PHY event routing, connection lookup, status and callback payload fields.',
               'limits': ['Uninitialized callback padding is excluded; child callback effects, final ROM placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
