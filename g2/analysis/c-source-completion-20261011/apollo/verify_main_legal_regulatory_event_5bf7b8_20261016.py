#!/usr/bin/env python3
"""Stock/C legal-regulatory callback comparison under controlled UI calls."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_event_5bf7b8.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-legal-regulatory-event-5bf7b8'
LOWER = {
    'audio_log_level': 0x43d0cf,
    'audio_log_extended': 0x43d575,
    'compressed_log_output': 0x43ce9f,
    'audio_legal_regulatory_build_5bf332': 0x5bf333,
    'audio_uart_page_58c238': 0x58c239,
    'audio_uart_lv_scroll_to_y_44ea04': 0x44ea05,
    'audio_legal_regulatory_root_200746a4': 0x200746a4,
    'audio_uart_registry_context_200014cc': 0x200014cc,
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'legal-regulatory.o', OUT / 'legal-regulatory-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    defs = [f'--defsym={name}=0x{value:x}' for name, value in LOWER.items()]
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', *defs, str(obj),
                    '-o', str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        sym = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return obj, elf, segs, sym['audio_uart_registry_callback_5bf7b8']

def run(stock, segments, entry, event, kind, target, mask, seed):
    image = PAYLOAD.read_bytes()[32:]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(image) + 4095) & ~4095)
    u.mem_write(0x438000, image)
    u.mem_map(0x100000, 0x20000)
    if not stock:
        for address, data in segments: u.mem_write(address, data)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(0x20008000, kind.to_bytes(4, 'little') + target.to_bytes(4, 'little'))
    u.mem_write(0x200746a4, (0x20063000 + seed).to_bytes(4, 'little'))
    u.mem_write(0x200014d0, (0x12345678 ^ seed).to_bytes(4, 'little'))
    for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                           A.UC_ARM_REG_R3), (event, 0x20008000, 8, 0x20072000 + seed)):
        u.reg_write(reg, value)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    trace, visited, done = [], set(), [False]
    def cstr(addr):
        if not addr: return None
        return bytes(u.mem_read(addr, 180)).split(b'\0', 1)[0].decode('utf-8', 'replace')
    def ret(uc): uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
    def code(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if stock and 0x5bf7b8 <= pc <= 0x5bf8a1: visited.add(pc)
        if pc == 0x43c0e4:
            dst, length, value = (uc.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            uc.mem_write(dst, bytes([value & 255]) * length); ret(uc)
        elif pc == 0x439be4:
            dst, src, length = (uc.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            uc.mem_write(dst, bytes(uc.mem_read(src, length))); ret(uc)
        elif pc == 0x43d0ce:
            trace.append(('mask',))
            uc.reg_write(A.UC_ARM_REG_R0, mask); ret(uc)
        elif pc == 0x43d574:
            sp = uc.reg_read(A.UC_ARM_REG_SP)
            line = int.from_bytes(uc.mem_read(sp, 4), 'little')
            fmt = int.from_bytes(uc.mem_read(sp + 4, 4), 'little')
            trace.append(('extended', uc.reg_read(A.UC_ARM_REG_R0),
                          cstr(uc.reg_read(A.UC_ARM_REG_R1)),
                          cstr(uc.reg_read(A.UC_ARM_REG_R2)),
                          cstr(uc.reg_read(A.UC_ARM_REG_R3)), line, cstr(fmt)))
            ret(uc)
        elif pc == 0x43ce9e:
            trace.append(('compact', uc.reg_read(A.UC_ARM_REG_R0),
                          cstr(uc.reg_read(A.UC_ARM_REG_R1)),
                          cstr(uc.reg_read(A.UC_ARM_REG_R2))))
            ret(uc)
        elif pc == 0x5bf332:
            trace.append(('build', uc.reg_read(A.UC_ARM_REG_R0)))
            uc.mem_write(0x200746a4, (0x20064000 + seed).to_bytes(4, 'little'))
            ret(uc)
        elif pc == 0x58c238:
            trace.append(('page', tuple(uc.reg_read(r) for r in
                                        (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            ret(uc)
        elif pc == 0x44ea04:
            trace.append(('scroll', tuple(uc.reg_read(r) for r in
                                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))))
            ret(uc)
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start((0x5bf7b8 if stock else entry) | 1, 0, count=2000)
    if not done[0]: raise RuntimeError('legal callback did not return')
    return {'trace': trace, 'return': u.reg_read(A.UC_ARM_REG_R0),
            'context': u.mem_read(0x200014d0, 4).hex(),
            'root': u.mem_read(0x200746a4, 4).hex()}, visited

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segs, entry = build()
    count, visited, logged = 0, set(), 0
    for event in (0, 1, 2, 3, 4, 5, 6):
        for kind in (0, 1, 2, 0xffffffff):
            for mask in (0, 1, 2, 4, 7):
                target = (0x1000 + event * 33 + kind) & 0xffffffff
                seed = (event + kind) & 15
                stock, hit = run(True, segs, entry, event, kind, target, mask, seed)
                source, _ = run(False, segs, entry, event, kind, target, mask, seed)
                if stock != source:
                    raise RuntimeError(f'legal mismatch {event=} {kind=} {mask=}: {stock} vs {source}')
                visited |= hit; count += 1; logged += sum(x[0] in ('extended', 'compact') for x in stock['trace'])
    receipt = {'status': 'PASS_NATIVE_MAIN_LEGAL_REGULATORY_EVENT_5BF7B8',
               'cases': count, 'visited_stock_instruction_addresses': len(visited),
               'controlled_log_calls': logged,
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['The page builder, scroll, page action, logging and memory helpers are controlled; final RAM allocation and whole-image link remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, len(visited), sha(path))

if __name__ == '__main__': main()
