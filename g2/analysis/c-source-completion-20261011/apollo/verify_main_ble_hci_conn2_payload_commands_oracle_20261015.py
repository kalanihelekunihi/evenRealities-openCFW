#!/usr/bin/env python3
"""Compare four compiled HCI command payload builders with pinned Apollo bodies."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_hci_conn2_payload_commands_52b0be.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-ble-hci-conn2-payload-commands'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NAMES = {
    'reply': ('audio_ble_hci_remote_conn_param_req_reply_52b0be', 0x52b0be, 7),
    'negative': ('audio_ble_hci_remote_conn_param_req_neg_reply_52b146', 0x52b146, 2),
    'data_len': ('audio_ble_hci_set_data_len_52b176', 0x52b176, 3),
    'auth_timeout': ('audio_ble_hci_write_auth_payload_timeout_52b70c', 0x52b70c, 2),
}
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *audio_ble_hci_cmd_alloc_52ae38(uint16_t a,uint16_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void audio_ble_hci_cmd_send(void*a){(void)a;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_hci_remote_conn_param_req_reply_52b0be',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, name, values, allocated):
            symbol, stock_entry, argc = NAMES[name]
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            cpu.mem_write(0x20001000, bytes((0xa5,) * 32))
            alloc_addr = (symbols['audio_ble_hci_cmd_alloc_52ae38'] & ~1) if compiled else 0x52ae38
            send_addr = (symbols['audio_ble_hci_cmd_send'] & ~1) if compiled else 0x52ae5e
            calls = []
            def hook(uc, addr, size, user):
                if addr == alloc_addr:
                    calls.append(('alloc', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xffff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if allocated else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == send_addr:
                    calls.append(('send', uc.reg_read(A.UC_ARM_REG_R0)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), values):
                cpu.reg_write(reg, value)
            sp = 0x2000ff00
            for index, value in enumerate(values[4:]):
                cpu.mem_write(sp + index * 4, value.to_bytes(4, 'little'))
            cpu.reg_write(A.UC_ARM_REG_SP, sp)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols[symbol] if compiled else stock_entry
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 32))

        vectors = ((0, 0, 0, 0, 0, 0, 0),
                   (1, 0x1234, 0xabcd, 0xff, 0x2345, 0x4567, 0x7fff),
                   (0xffff, 0xffff, 0x8000, 0x1357, 0x2468, 0xaaaa, 0x5555),
                   (0x100, 0x201, 0x302, 0x403, 0x504, 0x605, 0x706))
        cases = 0
        for name, (_, _, argc) in NAMES.items():
            for vector in vectors:
                for allocated in (False, True):
                    values = vector[:argc]
                    stock = run(False, name, values, allocated)
                    candidate = run(True, name, values, allocated)
                    if stock != candidate:
                        raise RuntimeError(f'{name=} {values=} {allocated=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HCI_CONN2_PAYLOAD_COMMANDS_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Four native command allocation opcodes/lengths, payload bytes, send calls, and allocation failures.',
               'limits': ['Allocator and send children are source-owned elsewhere; controller and physical link behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
