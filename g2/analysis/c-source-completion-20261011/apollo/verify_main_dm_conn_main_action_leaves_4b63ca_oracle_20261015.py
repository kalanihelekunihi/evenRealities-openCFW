#!/usr/bin/env python3
"""Compare compiled Cordio none/close action leaves with Apollo bytes."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_main_action_leaves_4b63ca.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-main-action-leaves-4b63ca'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void audio_ble_hci_disconnect_cmd_52af10(uint16_t h,uint8_t r){(void)h;(void)r;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    if blob[0x4b63ca - 0x438000:0x4b63d8 - 0x438000] != bytes.fromhex(
            '70 47 80 b5 09 79 80 89 74 f0 9d fd 01 bd'):
        raise RuntimeError('Cordio leaf instructions changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_sm_act_none_4b63ca',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, close, handle, reason):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb, message = bytearray(32), bytearray(32)
            ccb[12:14] = handle.to_bytes(2, 'little')
            message[4] = reason
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(message))
            calls = []
            target = (symbols['audio_ble_hci_disconnect_cmd_52af10'] & ~1) if compiled else 0x52af10
            def hook(uc, addr, size, user):
                if addr == target:
                    calls.append((uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xff))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            if compiled:
                name = 'audio_ble_dm_conn_sm_act_close_4b63cc' if close else 'audio_ble_dm_conn_sm_act_none_4b63ca'
                entry = symbols[name]
            else:
                entry = 0x4b63cc if close else 0x4b63ca
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 32)), bytes(cpu.mem_read(0x20002000, 32))

        cases = 0
        for handle in (0, 1, 0xff, 0x100, 0x1234, 0x7fff, 0xffff):
            for reason in (0, 1, 0x13, 0x3e, 0xff):
                for close in (False, True):
                    stock = run(False, close, handle, reason)
                    candidate = run(True, close, handle, reason)
                    if stock != candidate:
                        raise RuntimeError(f'close={close} handle={handle} reason={reason}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_ACTION_LEAVES_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native CCB/message memory and HCI disconnect call for none/close action leaves.',
               'limits': ['HCI disconnect child is a typed import; controller behavior and full connection action set remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
