#!/usr/bin/env python3
"""Compare complete legal-page builder call graph under named lower controls."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_page_build_5bf332.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-legal-page-build-5bf332'
HELPERS = {0x5bf114: 'audio_legal_regulatory_zero_styles_5bf114',
           0x5bf24e: 'audio_legal_regulatory_panel_5bf24e',
           0x5bf298: 'audio_legal_regulatory_label_5bf298',
           0x5bf2f8: 'audio_legal_regulatory_icon_5bf2f8'}
ARITY = {0x43de82:1, 0x43ded4:2, 0x43dfa4:2, 0x43f09a:3,
         0x43f4c0:3, 0x43f6b8:4, 0x43f6d6:5, 0x44104c:1,
         0x441246:3, 0x44127e:3, 0x44129e:3, 0x44131c:3,
         0x44133a:3, 0x441378:3, 0x441386:3, 0x4413be:3,
         0x44146a:3, 0x44e368:2, 0x44e3ca:2, 0x48ba78:2,
         0x48ba92:4, 0x5bf114:3, 0x5bf24e:1, 0x5bf298:2,
         0x5bf2f8:2}
RETURNS = {0x43de82, 0x44104c, 0x5bf24e, 0x5bf298, 0x5bf2f8}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'legal-page-build.o', OUT / 'legal-page-build-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    names = {f'audio_uart_page_{a:x}': a | 1 for a in ARITY if a not in HELPERS}
    names.update({name: a | 1 for a, name in HELPERS.items()})
    names['audio_legal_regulatory_root_200746a4'] = 0x200746a4
    names['audio_legal_asset_slots'] = 0x5bf8ac
    defs = [f'--defsym={name}=0x{value:x}' for name, value in sorted(names.items())]
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', *defs,
                    str(obj), '-o', str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        sym = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return obj, elf, segs, sym['audio_legal_regulatory_build_5bf332']

def run(stock, segments, entry, parent):
    image = PAYLOAD.read_bytes()[32:]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(image) + 4095) & ~4095)
    u.mem_write(0x438000, image)
    u.mem_map(0x100000, 0x30000)
    if not stock:
        for address, data in segments: u.mem_write(address, data)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(0x200746a4, (0x12345678).to_bytes(4, 'little'))
    u.reg_write(A.UC_ARM_REG_R0, parent)
    u.reg_write(A.UC_ARM_REG_R1, 0x11111111)
    u.reg_write(A.UC_ARM_REG_R2, 0x22222222)
    u.reg_write(A.UC_ARM_REG_R3, 0x33333333)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    trace, visited, done = [], set(), [False]
    def code(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if stock and 0x5bf332 <= pc <= 0x5bf7b7: visited.add(pc)
        if pc in ARITY:
            registers = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                         A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            args = tuple(uc.reg_read(r) for r in registers[:min(ARITY[pc], 4)])
            if ARITY[pc] == 5:
                args += (int.from_bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_SP), 4), 'little'),)
            trace.append((pc, args))
            if pc in RETURNS:
                uc.reg_write(A.UC_ARM_REG_R0, 0x20050000 + len(trace) * 0x40)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start((0x5bf332 if stock else entry) | 1, 0, count=10000)
    if not done[0]: raise RuntimeError('legal page builder did not return')
    return {'trace': trace, 'root': u.mem_read(0x200746a4, 4).hex(),
            'return': u.reg_read(A.UC_ARM_REG_R0)}, visited

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segs, entry = build()
    visited, count, calls = set(), 0, 0
    for parent in (0, 0x20004000, 0x2007abcd):
        stock, hit = run(True, segs, entry, parent)
        source, _ = run(False, segs, entry, parent)
        if stock != source:
            for i, (x, y) in enumerate(zip(stock['trace'], source['trace'])):
                if x != y:
                    raise RuntimeError(f'legal builder mismatch {parent=:x} call={i}: {x} vs {y}')
            raise RuntimeError(f'legal builder mismatch {parent=:x} calls={len(stock["trace"])}:{len(source["trace"])} state={stock["root"],stock["return"]} vs {source["root"],source["return"]}')
        visited |= hit; count += 1; calls += len(stock['trace'])
    receipt = {'status': 'PASS_NATIVE_MAIN_LEGAL_PAGE_BUILD_5BF332',
               'cases': count, 'controlled_lower_calls': calls,
               'visited_stock_instruction_addresses': len(visited),
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['Page, style, alignment and legal helper calls are controlled; resources are independently byte-checked C data; UI runtime and final placement remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, calls, len(visited), sha(path))

if __name__ == '__main__': main()
