#!/usr/bin/env python3
"""Compare native Cordio STK selection and security level with C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_smp_get_stk_537c4c.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/smp/smp_main.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-smp-get-stk-537c4c'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xfc];
__attribute__((noinline)) uint8_t *smpCcbByConnId(uint8_t x){(void)x;return 0;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'uint8_t *SmpDmGetStk(dmConnId_t connId, uint8_t *pSecLevel)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio SMP source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_smp_get_stk_537c4c',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, present, ready, supported, enabled, has_ltk,
                has_scratch, mitm, size_a, size_b):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            state = symbols['audio_ble_smp_handler_state'] if compiled else 0x20070aec
            cpu.mem_write(state, bytes(0xf8) + bytes((supported,)) + bytes(3))
            ccb = bytearray(0x50)
            ccb[0x24], ccb[0x2b] = size_a, size_b
            ccb[0x30:0x34] = (0x20006000 if has_scratch else 0).to_bytes(4, 'little')
            ccb[0x40], ccb[0x44] = (4 if mitm else 0), ready
            ccb[0x48:0x4c] = (0x20004000).to_bytes(4, 'little')
            cpu.mem_write(0x20003000, bytes(ccb))
            sc = bytearray(0x1c)
            sc[0] = enabled
            sc[0x18:0x1c] = (0x20005000 if has_ltk else 0).to_bytes(4, 'little')
            cpu.mem_write(0x20004000, bytes(sc))
            cpu.mem_write(0x20005000, bytes((0xa5,) * 64))
            cpu.mem_write(0x20006000, bytes((0x5a,) * 64))
            cpu.mem_write(0x20002000, bytes((0xe7,)))
            lookup = (symbols['smpCcbByConnId'] & ~1) if compiled else 0x5375fc
            calls = []
            def hook(uc, addr, size, user):
                if addr == lookup:
                    calls.append(('lookup', uc.reg_read(A.UC_ARM_REG_R0) & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20003000 if present else 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 2)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_smp_get_stk_537c4c'] if compiled else 0x537c4c
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(0x20002000, 1))

        cases = 0
        for present in (False, True):
            for ready in (0, 1):
                for supported in (0, 1):
                    for enabled in (0, 1):
                        for has_ltk in (False, True):
                            for has_scratch in (False, True):
                                for mitm in (False, True):
                                    for size_a, size_b in ((16, 16), (8, 16), (16, 8)):
                                        stock = run(False, present, ready, supported, enabled,
                                                    has_ltk, has_scratch, mitm, size_a, size_b)
                                        candidate = run(True, present, ready, supported, enabled,
                                                        has_ltk, has_scratch, mitm, size_a, size_b)
                                        if stock != candidate:
                                            raise RuntimeError(f'{present=} {ready=} {supported=} {enabled=} {has_ltk=} {has_scratch=} {mitm=} {size_a=} {size_b=}: {stock} != {candidate}')
                                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SMP_GET_STK_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native SMP CCB lookup, key-ready gate, SC and legacy STK selection and security level.',
               'limits': ['Only valid non-null SC CCB contexts are compared; final RAM placement and cryptographic use remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
