#!/usr/bin/env python3
"""Compare common-button fade-in/out descriptor setup with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/terminal_list_anim_fade_start_58c622.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-terminal-list-anim-fade-start-58c622'
LOWER = {
    'audio_log_flags': 0x43d0cf,
    'audio_log_extended': 0x43d575,
    'compressed_log_output': 0x43ce9f,
    'audio_uart_lv_style_unlink_450500': 0x450501,
    'audio_uart_lv_anim_init_4503d6': 0x4503d7,
    'audio_uart_lv_anim_values_4506ce': 0x4506cf,
    'audio_uart_lv_anim_start_450408': 0x450409,
    'audio_terminal_button_fade_callback_58c230': 0x58c231,
    'audio_uart_lv_anim_path_450688': 0x450689,
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'terminal-list-anim-fade-start.o', OUT / 'terminal-list-anim-fade-start-oracle.elf'
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
    return obj, elf, segs, {kind: sym[f'audio_terminal_list_anim_{kind}_start_{address:x}'] for kind, address in (('new', 0x58c622), ('old', 0x58c6c4))}

def run(stock, segments, entries, kind, obj, duration, complete, mask):
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
                           A.UC_ARM_REG_R3), (obj, duration, complete, 0xa5a5a5a5)):
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
        if stock and 0x58c622 <= pc <= 0x58c728: visited.add(pc)
        if pc == 0x43d0ce:
            trace.append(('mask',)); uc.reg_write(A.UC_ARM_REG_R0, mask); ret(uc)
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
                          cstr(uc.reg_read(A.UC_ARM_REG_R1))))
            ret(uc)
        elif pc == 0x450500:
            trace.append(('unlink', uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1)))
            uc.reg_write(A.UC_ARM_REG_R0, 0); ret(uc)
        elif pc == 0x4503d6:
            addr = uc.reg_read(A.UC_ARM_REG_R0)
            uc.mem_write(addr, bytes(0x60)); trace.append(('init',)); ret(uc)
        elif pc == 0x4506ce:
            addr = uc.reg_read(A.UC_ARM_REG_R0)
            a = uc.reg_read(A.UC_ARM_REG_R1); b = uc.reg_read(A.UC_ARM_REG_R2)
            uc.mem_write(addr + 0x24, a.to_bytes(4, 'little'))
            uc.mem_write(addr + 0x28, (0x80000000).to_bytes(4, 'little'))
            uc.mem_write(addr + 0x2c, b.to_bytes(4, 'little'))
            trace.append(('values', a, b)); ret(uc)
        elif pc == 0x450408:
            addr = uc.reg_read(A.UC_ARM_REG_R0)
            trace.append(('start', bytes(uc.mem_read(addr, 0x60)).hex()))
            uc.reg_write(A.UC_ARM_REG_R0, 0x20080000); ret(uc)
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(((0x58c622 if kind == 'new' else 0x58c6c4) if stock else entries[kind]) | 1, 0, count=2000)
    if not done[0]: raise RuntimeError('list animation fade did not return')
    return trace, visited

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segs, entries = build()
    visited, count = set(), 0
    for kind in ('new', 'old'):
      for page in (0, 0x20064000, 0x20064004):
         for duration in (0, 1, 200, 250, 0xffffffff):
              for complete in (0, 1, 0xff, 0x12345678):
                   for mask in (0, 1, 2, 4, 7):
                        stock, hit = run(True, segs, entries, kind, page, duration, complete, mask)
                        source, _ = run(False, segs, entries, kind, page, duration, complete, mask)
                        if stock != source:
                              for i, (x, y) in enumerate(zip(stock, source)):
                                   if x != y:
                                        raise RuntimeError(f'list fade mismatch {kind=} {page=} {duration=} {complete=} {mask=} item={i}: {x} vs {y}')
                              raise RuntimeError(f'list fade trace length mismatch {len(stock)} vs {len(source)}')
                        count += 1; visited |= hit
    receipt = {'status': 'PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_FADE_START_C_ORACLE',
               'cases': count, 'visited_stock_instruction_addresses': len(visited),
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['Animation descriptor and logging branches are controlled; callback body and runtime effects remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, len(visited), sha(path))

if __name__ == '__main__': main()
