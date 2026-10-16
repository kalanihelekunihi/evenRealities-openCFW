#!/usr/bin/env python3
"""Compare two small legal fade callbacks with native lower-call traces."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_fade_helpers.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-legal-fade-helpers'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'legal-fade-helpers.o', OUT / 'legal-fade-helpers-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    '--defsym=audio_uart_display_audio_reset_441488=0x441489',
                    '--defsym=audio_uart_lv_anim_bezier_450a04=0x450a05',
                    str(obj), '-o', str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        sym = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return obj, elf, segs, sym

def run(stock, segments, entry, args):
    image = PAYLOAD.read_bytes()[32:]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(image) + 4095) & ~4095)
    u.mem_write(0x438000, image)
    u.mem_map(0x100000, 0x20000)
    if not stock:
        for address, data in segments: u.mem_write(address, data)
    u.mem_map(0x20000000, 0x100000)
    for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                           A.UC_ARM_REG_R3), args):
        u.reg_write(reg, value)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    trace, done = [], [False]
    def code(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if pc == 0x441488:
            trace.append(('alpha', tuple(uc.reg_read(r) for r in
                                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
        elif pc == 0x450a04:
            sp = uc.reg_read(A.UC_ARM_REG_SP)
            trace.append(('path', tuple(uc.reg_read(r) for r in
                                        (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                         A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)) +
                          (int.from_bytes(uc.mem_read(sp, 4), 'little'),)))
            uc.reg_write(A.UC_ARM_REG_R0, 0x12345678)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=200)
    if not done[0]: raise RuntimeError('fade helper did not return')
    return trace, u.reg_read(A.UC_ARM_REG_R0)

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segs, sym = build()
    count = 0
    for name, addr in (('audio_legal_regulatory_fade_callback_58c12c', 0x58c12c),
                       ('audio_uart_lv_anim_path_45065a', 0x45065a)):
        for value in (0, 1, 2, 0x7f, 0xff, 0x100, 0x12345678, 0xffffffff):
            for ptr in (0x20004000, 0x20005000, 0x20006000, 0x20007000):
                args = (ptr, value, value ^ 0x55555555, value ^ 0xaaaaaaaa)
                stock = run(True, segs, addr, args)
                source = run(False, segs, sym[name], args)
                if stock[0] != source[0] or (addr == 0x45065a and stock[1] != source[1]):
                    raise RuntimeError(f'fade helper mismatch {name} {value:x}: {stock} vs {source}')
                count += 1
    receipt = {'status': 'PASS_NATIVE_MAIN_LEGAL_FADE_HELPERS', 'cases': count,
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['The alpha setter and Bezier provider are controlled; runtime animation scheduling is not proved.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, sha(path))

if __name__ == '__main__': main()
