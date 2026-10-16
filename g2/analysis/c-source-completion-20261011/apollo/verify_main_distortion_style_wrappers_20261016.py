#!/usr/bin/env python3
"""Native/C style-operation trace for six distortion-screen page wrappers."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_distortion_style_wrappers.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261016/main-distortion-style-wrappers'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
WRAPPERS = (0x441246, 0x441254, 0x44130c, 0x44142e, 0x48ba78, 0x48ba92)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'distortion-style-wrappers.o'
    elf = OUT / 'distortion-style-wrappers-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SRC), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    '--defsym=audio_uart_page_style_apply_44be4c=0x44be4d',
                    str(obj), '-o', str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return obj, elf, segments, symbols

def execute(stock, segments, entry, args):
    image = PAYLOAD.read_bytes()[32:]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(image) + 4095) & ~4095)
    u.mem_write(0x438000, image)
    u.mem_map(0x100000, 0x20000)
    if not stock:
        for address, data in segments: u.mem_write(address, data)
    u.mem_map(0x20000000, 0x100000)
    for register, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), args):
        u.reg_write(register, value)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    calls, done = [], [False]
    def hook(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if pc == 0x44be4c:
            calls.append(tuple(uc.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                        A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)))
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start(entry | 1, 0, count=500)
    if not done[0]: raise RuntimeError('style wrapper did not return')
    return calls

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segments, symbols = build()
    cases, lower = 0, 0
    for address in WRAPPERS:
        entry = symbols[f'audio_uart_page_{address:x}']
        for value in (0, 1, 2, 4, 0x7f, 0xff, 0x1234, 0xffffffff):
            args = (0x20020000, value, value ^ 0xa5a5a5a5, (value + 7) & 0xffffffff)
            stock = execute(True, segments, address, args)
            source = execute(False, segments, entry, args)
            if stock != source:
                raise RuntimeError(f'style mismatch at {address:x} value={value:x}: {stock} vs {source}')
            cases += 1; lower += len(stock)
    receipt = {'status': 'PASS_NATIVE_MAIN_DISTORTION_STYLE_WRAPPERS',
               'cases': cases, 'controlled_style_apply_calls': lower,
               'wrappers': [f'0x{x:06x}' for x in WRAPPERS],
               'source': str(SRC.relative_to(ROOT)), 'source_sha256': sha(SRC),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['The 0x44be4c style provider is controlled; page-object and hardware behavior remain outside this oracle.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, lower, sha(path))

if __name__ == '__main__': main()
