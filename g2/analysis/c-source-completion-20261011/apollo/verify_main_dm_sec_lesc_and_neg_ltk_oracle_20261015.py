#!/usr/bin/env python3
"""Compare native LESC flag query and negative LTK HCI command to C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_sec_lesc_and_neg_ltk.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-sec-lesc-neg-ltk'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) uint8_t *smpCcbByConnId(uint8_t x){(void)x;return 0;}
__attribute__((noinline)) void *audio_ble_hci_cmd_alloc_52ae38(uint16_t a,uint16_t b){(void)a;(void)b;return 0;}
__attribute__((noinline)) void audio_ble_hci_cmd_send(void *p){(void)p;}
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
                        '-Wl,-e,audio_ble_smp_lesc_enabled_537c30',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, kind, ccb_present, sc_present, flag, allocated, handle):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            ccb = bytearray(0x50)
            ccb[0x48:0x4c] = (0x20004000 if sc_present else 0).to_bytes(4, 'little')
            cpu.mem_write(0x20003000, bytes(ccb))
            cpu.mem_write(0x20004000, bytes((flag,)))
            cpu.mem_write(0x20002000, bytes((0xa5,) * 16))
            lookup = (symbols['smpCcbByConnId'] & ~1) if compiled else 0x5375fc
            alloc = (symbols['audio_ble_hci_cmd_alloc_52ae38'] & ~1) if compiled else 0x52ae38
            send = (symbols['audio_ble_hci_cmd_send'] & ~1) if compiled else 0x52ae5e
            calls = []
            def hook(uc, addr, size, user):
                if addr == lookup:
                    calls.append(('lookup', uc.reg_read(A.UC_ARM_REG_R0) & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20003000 if ccb_present else 0)
                elif addr == alloc:
                    calls.append(('alloc', uc.reg_read(A.UC_ARM_REG_R0) & 0xffff,
                                  uc.reg_read(A.UC_ARM_REG_R1) & 0xffff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20002000 if allocated else 0)
                elif addr == send:
                    p = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('send', bytes(uc.mem_read(p + 3, 2)).hex()))
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 3 if kind == 'lesc' else handle)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = ((symbols['audio_ble_smp_lesc_enabled_537c30'] if kind == 'lesc' else
                      symbols['HciLeLtkReqNegReplCmd']) if compiled else
                     (0x537c30 if kind == 'lesc' else 0x52b2a4))
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            result = cpu.reg_read(A.UC_ARM_REG_R0) & 0xff if kind == 'lesc' else None
            return calls, result

        cases = 0
        for ccb_present in (False, True):
            for sc_present in (False, True):
                for flag in (0, 1, 0xff):
                    stock = run(False, 'lesc', ccb_present, sc_present, flag, False, 0)
                    candidate = run(True, 'lesc', ccb_present, sc_present, flag, False, 0)
                    if stock != candidate:
                        raise RuntimeError(f'LESC {ccb_present=} {sc_present=} {flag=}: {stock} != {candidate}')
                    cases += 1
        for allocated in (False, True):
            for handle in (0, 0x1234, 0xffff):
                stock = run(False, 'neg', False, False, 0, allocated, handle)
                candidate = run(True, 'neg', False, False, 0, allocated, handle)
                if stock != candidate:
                    raise RuntimeError(f'negative LTK {allocated=} {handle=}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_SEC_LESC_NEG_LTK_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native SMP CCB/SC flag lookup and negative LTK HCI allocation/payload/send.',
               'limits': ['Controller effects and final RAM placement remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
