#!/usr/bin/env python3
"""Compare native and C DM HCI dispatch routing and state changes."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_hci_handler_53694c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-hci-handler-53694c'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_stack_rows_200738dc[0x20];
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) void audio_ble_dm_stack_hci_scan_complete_5368b6(void *p){(void)p;}
__attribute__((noinline)) void WsfTimerStartMs(void *p,uint32_t ms){(void)p;(void)ms;}
__attribute__((noinline)) void WsfTimerStop(void *p){(void)p;}
__attribute__((noinline)) void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t a,uint8_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
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
                        '-Wl,-e,audio_ble_dm_stack_hci_handler_53694c',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        names = {
            'scan': ('audio_ble_dm_stack_hci_scan_complete_5368b6', 0x5368b6),
            'start': ('WsfTimerStartMs', 0x52a4c4),
            'stop': ('WsfTimerStop', 0x52a4d2),
            'priv': ('audio_ble_dm_dev_pass_priv_4b2ea6', 0x4b2ea6),
        }

        def run(compiled, code, state, status, timeout):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            rows = symbols['audio_ble_dm_stack_rows_200738dc'] if compiled else 0x200738dc
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            initial = bytearray((i * 11 + 0x3a) & 0xff for i in range(32))
            initial[0x18] = state
            initial[0x1a:0x1c] = timeout.to_bytes(2, 'little')
            cpu.mem_write(rows, bytes(initial))
            cpu.mem_write(dm, bytes(24))
            cpu.mem_write(dm + 8, (0x110001).to_bytes(4, 'little'))
            event = bytearray((i * 13 + 0x27) & 0xff for i in range(16))
            event[2], event[3] = code, status
            cpu.mem_write(0x20001000, bytes(event))
            addr_to_name = {((symbols[sym] if compiled else stock) & ~1): name
                            for name, (sym, stock) in names.items()}
            calls = []
            def hook(uc, addr, size, user):
                if addr == 0x110000:
                    calls.append(('callback', uc.reg_read(A.UC_ARM_REG_R0)))
                elif addr in addr_to_name:
                    name = addr_to_name[addr]
                    args = tuple(uc.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4))
                    if name in ('scan', 'start', 'stop'):
                        args = (args[0] - (rows if name != 'scan' else 0x20001000),) + (() if name != 'start' else (args[1],))
                    elif name == 'priv':
                        args = (args[0] & 0xff, args[1] & 0xff, args[2], args[3])
                    calls.append((name,) + args)
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_stack_hci_handler_53694c'] if compiled else 0x53694c
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(rows, 32)), bytes(cpu.mem_read(0x20001000, 16))

        cases = 0
        for code in (6, 0x34, 0x24, 0x25, 0x35):
            for state in (0, 1, 2, 3):
                for status in (0, 1):
                    for timeout in (0, 30):
                        stock = run(False, code, state, status, timeout)
                        candidate = run(True, code, state, status, timeout)
                        if stock != candidate:
                            raise RuntimeError(f'{code=} {state=} {status=} {timeout=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native scan child routing, HCI event state changes, timer calls, privacy pass and callback.',
               'limits': ['Scan-complete child effects and final controller behavior are separate obligations.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
