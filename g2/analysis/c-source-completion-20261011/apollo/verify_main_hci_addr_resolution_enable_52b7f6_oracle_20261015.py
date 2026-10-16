#!/usr/bin/env python3
"""Compare native HCI address-resolution-enable command construction to C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_hci_addr_resolution_enable_52b7f6.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/hci/dual_chip/hci_cmd.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-hci-addr-resolution-enable-52b7f6'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) uint8_t *hciCmdAlloc(uint16_t a,uint8_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void hciCmdSend(uint8_t *p){(void)p;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void HciLeSetAddrResolutionEnable(uint8_t enable)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,HciLeSetAddrResolutionEnable', str(SOURCE), str(shim),
                        '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, enabled, available, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            cpu.mem_write(0x20001000, bytes((seed + i * 7) & 0xff for i in range(16)))
            alloc = (symbols['hciCmdAlloc'] if compiled else 0x52ae38) & ~1
            send = (symbols['hciCmdSend'] if compiled else 0x52ae5e) & ~1
            calls = []
            def hook(uc, addr, size, user):
                if addr == alloc:
                    calls.append(('alloc', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if available else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == send:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('send', bytes(uc.mem_read(ptr, 16)).hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, enabled)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['HciLeSetAddrResolutionEnable'] if compiled else 0x52b7f6
            cpu.emu_start(entry | 1, 0x600000, count=300)
            return calls, bytes(cpu.mem_read(0x20001000, 16))
        cases = 0
        for enabled in (0, 1, 0xff):
            for available in (False, True):
                for seed in (0, 0xa5):
                    stock = run(False, enabled, available, seed)
                    candidate = run(True, enabled, available, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{enabled=} {available=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HCI_ADDR_RES_ENABLE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Opcode 0x202d, one-byte allocation, absent-buffer behavior, command byte and send payload.',
               'limits': ['Transport send effects and physical controller behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
