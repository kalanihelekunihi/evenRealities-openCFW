#!/usr/bin/env python3
"""Compare compiled Cordio connection HCI routing with pinned Apollo Main."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_hci_handler_4b68a4.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-hci-handler-4b68a4'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *audio_ble_dm_conn_ccb_by_address_4b6170(const void*a){(void)a;return 0;}
__attribute__((noinline)) void *audio_ble_dm_conn_complete_states_4b5b24(void){return 0;}
__attribute__((noinline)) void *audio_ble_dm_conn_ccb_alloc_4b5c78(const void*a){(void)a;return 0;}
__attribute__((noinline)) void *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t a){(void)a;return 0;}
__attribute__((noinline)) void audio_ble_dm_conn_sm_execute_533ef4(void*a,void*b){(void)a;(void)b;}
'''
CHILDREN = {
    'address': ('audio_ble_dm_conn_ccb_by_address_4b6170', 0x4b6170),
    'states': ('audio_ble_dm_conn_complete_states_4b5b24', 0x4b5b24),
    'alloc': ('audio_ble_dm_conn_ccb_alloc_4b5c78', 0x4b5c78),
    'handle': ('audio_ble_dm_conn_ccb_by_handle_4b601c', 0x4b601c),
    'execute': ('audio_ble_dm_conn_sm_execute_533ef4', 0x533ef4),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConnHciHandler(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('dmConnCcbByBdAddr', 'dmConnCmplStates', 'dmConnCcbAlloc',
                 'dmConnCcbByHandle', 'dmConnSmExecute'):
        if term not in body:
            raise RuntimeError('Cordio HCI routing source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_hci_handler_4b68a4',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, status, role, outcome, conn_id):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytearray((i * 3 + 7) & 0xff for i in range(64))
            ccb[0x10] = conn_id
            msg = bytearray((i * 5 + 0x21) & 0xff for i in range(64))
            msg[:2] = b'\x34\x12'
            msg[2] = event
            msg[3] = status
            msg[8] = role
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(msg))
            addresses = {(symbols[symbol] & ~1) if compiled else stock: label
                         for label, (symbol, stock) in CHILDREN.items()}
            calls = []
            def hook(uc, addr, size, user):
                label = addresses.get(addr)
                if label is None:
                    return
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                if label == 'address':
                    calls.append((label, a - 0x20002000))
                    result = outcome == 0
                elif label == 'states':
                    calls.append((label,))
                    result = outcome == 1
                elif label == 'alloc':
                    calls.append((label, a - 0x20002000))
                    result = outcome == 2
                elif label == 'handle':
                    calls.append((label, a))
                    result = outcome in (0, 2)
                else:
                    calls.append((label, a, b, bytes(uc.mem_read(0x20002000, 64))))
                    result = None
                if result is not None:
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if result else 0)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_hci_handler_4b68a4'] if compiled else 0x4b68a4
            cpu.emu_start(entry | 1, 0x600000, count=500)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for event in (1, 2, 3, 0x47, 0xff):
            for status in (0, 1):
                for role in (0, 1):
                    for outcome in range(4):
                        for conn_id in (0, 0x7f, 0xff):
                            stock = run(False, event, status, role, outcome, conn_id)
                            candidate = run(True, event, status, role, outcome, conn_id)
                            if stock != candidate:
                                raise RuntimeError(f'{event=} {status=} {role=} {outcome=} {conn_id=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_HCI_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native CCB lookup/allocate call order, event/parameter mutation and state-machine forwarding.',
               'limits': ['Five helper effects are cut at native call boundaries; lookup, allocation and state machine bodies remain separate obligations.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
