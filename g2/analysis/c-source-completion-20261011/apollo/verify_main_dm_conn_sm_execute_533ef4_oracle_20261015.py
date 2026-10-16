#!/usr/bin/env python3
"""Compare compiled Cordio connection state machine with pinned Apollo Main."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_sm_execute_533ef4.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn_sm.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-sm-execute-533ef4'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_master_state_a[12];
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
    for term in ('dmConnStateTbl[DM_CONN_SM_NUM_STATES]', 'DM_CONN_NEXT_STATE',
                 'DM_CONN_ACTION', 'DM_CONN_ACT_SET_ID(action)',
                 'DM_CONN_ACT_ID(action)', 'void dmConnSmExecute('):
        if term not in upstream:
            raise RuntimeError('Cordio state-machine source changed')
    stock_table = blob[0x6ecc58 - 0x438000:0x6ecc58 - 0x438000 + 80]
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_sm_execute_533ef4',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        table_address = symbols['audio_ble_dm_conn_sm_state_table_6ecc58']
        candidate_table = next(seg[table_address - address:table_address - address + 80]
                               for address, seg in segments
                               if address <= table_address < address + len(seg))
        if candidate_table != stock_table:
            raise RuntimeError('compiled state table differs from stock 80 bytes')

        def run(compiled, state, event, active, vendor, flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x80000)
            ccb = bytearray((i * 3 + 7) & 0xff for i in range(64))
            ccb[0x15] = state
            msg = bytearray((i * 5 + 0x21) & 0xff for i in range(64))
            msg[2] = event
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(msg))
            set_base = symbols['audio_ble_dm_master_state_a'] if compiled else 0x20073fe4
            for set_id in range(3):
                table = 0x20004000 + set_id * 0x40
                cpu.mem_write(set_base + set_id * 4,
                              (table if active else 0).to_bytes(4, 'little'))
                for action_id in range(16):
                    handler = 0x20005000 + set_id * 0x100 + action_id * 4
                    cpu.mem_write(table + action_id * 4, (handler | 1).to_bytes(4, 'little'))
                    cpu.mem_write(handler, b'\x70\x47')
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
                if 0x20005000 <= address < 0x20005300 and (address - 0x20005000) % 4 == 0:
                    set_id = (address - 0x20005000) // 0x100
                    action_id = ((address - 0x20005000) % 0x100) // 4
                    calls.append(('action', set_id, action_id,
                                  uc.reg_read(A.UC_ARM_REG_R0),
                                  uc.reg_read(A.UC_ARM_REG_R1)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                    return
                kind = addresses.get(address)
                if kind is None:
                    return
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                c = uc.reg_read(A.UC_ARM_REG_R2)
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                if kind == 'vendor':
                    uc.reg_write(A.UC_ARM_REG_R0, vendor)
                elif kind == 'compare':
                    left = string(a)
                    right = string(b)
                    uc.reg_write(A.UC_ARM_REG_R0, 0 if left[:c] == right[:c] else 1)
                elif kind == 'flags':
                    uc.reg_write(A.UC_ARM_REG_R0, flags)
                elif kind == 'wsf':
                    fmt = string(b)
                    n = fmt.count('%d')
                    values = [c, uc.reg_read(A.UC_ARM_REG_R3)]
                    if n > 2:
                        values.append(int.from_bytes(uc.mem_read(sp, 4), 'little'))
                    calls.append(('wsf', string(a), fmt, tuple(values[:n])))
                else:
                    fmt = string(int.from_bytes(uc.mem_read(sp + 4, 4), 'little'))
                    n = fmt.count('%d')
                    values = [int.from_bytes(uc.mem_read(sp + 8 + 4 * i, 4), 'little')
                              for i in range(n)]
                    calls.append(('extended', a & 0xff, string(b), string(c),
                                  string(uc.reg_read(A.UC_ARM_REG_R3)),
                                  int.from_bytes(uc.mem_read(sp, 4), 'little'),
                                  fmt, tuple(values)))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2007ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_sm_execute_533ef4'] if compiled else 0x533ef4
            cpu.emu_start(entry | 1, 0x600000, count=30000)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for state in range(5):
            for event_low in range(8):
                for event_high in (0, 0x80):
                    for active in (False, True):
                        for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                            event = event_low | event_high
                            stock = run(False, state, event, active, vendor, flags)
                            candidate = run(True, state, event, active, vendor, flags)
                            if stock != candidate:
                                raise RuntimeError(f'{state=} {event=} {active=} {vendor=} {flags=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_SM_EXECUTE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'stock_table_hex': stock_table.hex(), 'cases': cases,
               'comparison_scope': 'All five states and eight event columns, high-bit masking, null/active action sets, stock trace calls, CCB transition and indirect dispatch.',
               'limits': ['Action bodies and logger effects are cut at native call boundaries.',
                          'Out-of-range CCB states are outside the table contract and are not claimed.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
