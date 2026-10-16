#!/usr/bin/env python3
"""Compare legal-page helper C against stock lower-call and return contracts."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_page_helpers.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-legal-page-helpers'
FUNCS = (
    ('audio_uart_page_4413be', 0x4413be),
    ('audio_uart_page_4413ce', 0x4413ce),
    ('audio_uart_page_44144c', 0x44144c),
    ('audio_legal_regulatory_zero_styles_5bf114', 0x5bf114),
    ('audio_legal_regulatory_panel_5bf24e', 0x5bf24e),
    ('audio_legal_regulatory_label_5bf298', 0x5bf298),
    ('audio_legal_regulatory_icon_5bf2f8', 0x5bf2f8),
)
LOWERS = (0x43de82, 0x43dfa4, 0x43f4c0, 0x44104c, 0x44120e,
          0x44121c, 0x44122a, 0x441238, 0x44127e, 0x44129e,
          0x44131c, 0x44140e, 0x44143e, 0x44145a, 0x44146a,
          0x498668, 0x498680, 0x499416, 0x49942e, 0x44be4c)
RETURNS = {0x43de82, 0x44104c, 0x498668, 0x499416}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'legal-page-helpers.o', OUT / 'legal-page-helpers-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    defs = [f'--defsym=audio_uart_page_{a:x}=0x{a|1:x}' for a in LOWERS if a != 0x44be4c]
    defs += ['--defsym=audio_uart_page_style_apply_44be4c=0x44be4d',
             '--defsym=audio_uart_ring_primary_head_cell=0x200746dc']
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', *defs,
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
    u.mem_write(0x200746dc, (0x20010000).to_bytes(4, 'little'))
    u.mem_write(0x2001000c, (7).to_bytes(4, 'little'))
    for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                           A.UC_ARM_REG_R3), args):
        u.reg_write(reg, value)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    trace, done = [], [False]
    def code(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if pc in LOWERS:
            trace.append((pc, tuple(uc.reg_read(r) for r in
                                    (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            if pc in RETURNS:
                uc.reg_write(A.UC_ARM_REG_R0, 0x20050000 + len(trace) * 0x40)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=2000)
    if not done[0]: raise RuntimeError('legal page helper did not return')
    return trace, (u.reg_read(A.UC_ARM_REG_R0), u.reg_read(A.UC_ARM_REG_R1))

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segs, sym = build()
    count, lower = 0, 0
    for name, address in FUNCS:
        for value in (0, 1, 2, 7, 0x7f, 0xff, 0x1234, 0xffffffff):
            for parent in (0x20002000, 0x20003000):
                args = (parent, value, value ^ 0xa5a5a5a5, 0x12345678)
                stock = run(True, segs, address, args)
                source = run(False, segs, sym[name], args)
                if stock[0] != source[0] or (address in (0x5bf24e, 0x5bf298, 0x5bf2f8)
                                             and stock[1] != source[1]):
                    for i, (x, y) in enumerate(zip(stock[0], source[0])):
                        if x != y:
                            raise RuntimeError(f'legal helper mismatch {name} {value:x} call {i}: {x} vs {y}')
                    raise RuntimeError(f'legal helper mismatch {name} {value:x}: {stock} vs {source}')
                count += 1; lower += len(stock[0])
    receipt = {'status': 'PASS_NATIVE_MAIN_LEGAL_PAGE_HELPERS',
               'cases': count, 'controlled_lower_calls': lower,
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['Page creation, style, text and bitmap children are controlled; stock assets and final RAM placement remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, lower, sha(path))

if __name__ == '__main__': main()
