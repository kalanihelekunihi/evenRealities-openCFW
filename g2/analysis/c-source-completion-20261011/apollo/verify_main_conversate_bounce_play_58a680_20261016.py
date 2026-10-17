#!/usr/bin/env python3
"""Stock/C lower-call replay for bounce_animation_play and its verified stop child."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCES = [G2 / 'components/audio/uart_thread_source_candidate/' / name for name in
           ('conversate_bounce_stop_58a7d2.c', 'conversate_bounce_play_58a680.c')]
STOCK = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261016/main-conversate-bounce-play-58a680'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
LOWERS = {'audio_uart_page_43f142': (0x101010, 0x43f142, 'set_y'),
          'audio_uart_lv_style_unlink_450500': (0x101020, 0x450500, 'unlink'),
          'audio_log_flags': (0x101030, 0x43d0ce, 'flags'),
          'audio_log_extended': (0x101040, 0x43d574, 'extended'),
          'compressed_log_output': (0x101050, 0x43ce9e, 'compact'),
          'audio_uart_lv_anim_init_4503d6': (0x101060, 0x4503d6, 'anim_init'),
          'audio_uart_lv_anim_values_4506ce': (0x101070, 0x4506ce, 'values'),
          'audio_uart_lv_anim_start_450408': (0x101080, 0x450408, 'anim_start')}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    objects = []
    for index, source in enumerate(SOURCES):
        obj = OUT / f'oracle-{index}.o'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding',
                        '-fno-builtin', '-c', str(source), '-o', str(obj)], check=True)
        objects.append(obj)
    elf_path = OUT / 'oracle.elf'
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-e',
                    'audio_conversate_main_list_scroll_58a680',
                    '--defsym=audio_uart_lv_anim_path_450672=0x450673',
                    '--defsym=audio_conversate_bounce_y_58a3fc=0x58a3fd',
                    '--defsym=audio_conversate_bounce_phase1_done_58a408=0x58a409',
                    *[f'--defsym={name}=0x{row[0]|1:x}' for name, row in LOWERS.items()],
                    *map(str, objects), '-o', str(elf_path)], check=True, capture_output=True)
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments()
                    if p['p_type'] == 'PT_LOAD' and p['p_vaddr'] < 0x20000000]
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(native, object_, active, y, direction, extra, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        state = 0x20073e14 if native else symbols['audio_conversate_bounce_state_20073e14']
        cpu.mem_write(state, struct.pack('<IIII', active, 37, 0x12345678, 0x9abcdef0))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        for register, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                   (object_, y, direction, extra)):
            cpu.reg_write(register, value)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}
        def cstr(machine, address):
            return bytes(machine.mem_read(address, 200)).split(b'\0', 1)[0].decode()
        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            if kind in ('set_y', 'unlink'):
                events.append((kind, *r[:2]))
            elif kind == 'values': events.append((kind, r[1], r[2]))
            elif kind == 'flags': events.append((kind,))
            elif kind == 'extended':
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, message = struct.unpack('<II', machine.mem_read(sp, 8))
                argc = 1 if line in (0xe2, 0xc7) else 3 if line == 0xb9 else 0
                args = struct.unpack('<' + 'I'*argc, machine.mem_read(sp+8, 4*argc)) if argc else ()
                if line == 0xb9: args = (cstr(machine, args[0]), *args[1:])
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, message), *args))
            elif kind == 'compact':
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                mask = r[0]
                argc = 2 if mask == 0x0cc00000 else 0
                args = struct.unpack('<' + 'I'*argc, machine.mem_read(sp, 4*argc)) if argc else ()
                if mask == 0x0cc00000: args = (cstr(machine, r[3]), *args)
                events.append((kind, mask, cstr(machine, r[1]), cstr(machine, r[2]),
                               *(args if argc else (() if mask == 0x04000000 or mask == 0x10000000 else (r[3],)))))
            elif kind == 'anim_init':
                events.append((kind,))
                machine.mem_write(r[0], bytes(96))
            elif kind == 'anim_start':
                words = struct.unpack('<13I', machine.mem_read(r[0], 52))
                events.append((kind, words[0], words[1], words[4], words[7] == state,
                               words[8], words[12], *words[10:12]))
            else: events.append((kind,))
            machine.reg_write(A.UC_ARM_REG_R0, flags if kind == 'flags' else 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x58a680 if native else symbols['audio_conversate_main_list_scroll_58a680']
        cpu.emu_start(entry | 1, 0, count=900)
        if not done[0]: raise RuntimeError('bounce play did not return')
        return events, bytes(cpu.mem_read(state, 16))
    cases = [(object_, active, y, direction, extra, flags)
             for object_ in (0, 0x20001000)
             for active in (0, 0x20001000, 0x20002000)
             for y in (0, 40, 0xfffffff0)
             for direction in (0, 1, 0x100)
             for extra in (0, 0x1234)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        actual, expected = run(False, *case), run(True, *case)
        if actual != expected:
            raise RuntimeError(f'bounce play mismatch {case}: {expected} != {actual}')
    record = {'status': 'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PLAY_58A680_C',
              'stock_payload_sha256': PAYLOAD_SHA, 'cases': len(cases),
              'native_body': '0x58a680..0x58a7d1',
              'sources': [str(p.relative_to(ROOT)) for p in SOURCES],
              'source_sha256': [hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES],
              'oracle_elf': str(elf_path.relative_to(ROOT)),
              'oracle_elf_sha256': hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              'source_complete': False, 'flashable': False, 'hardware_proof': False,
              'limits': ['Animation callbacks, LVGL and log functions remain lower boundaries.',
                         'The final linker must place bounce state at 0x20073e14.']}
    receipt = OUT / 'oracle-receipt.json'
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())

if __name__ == '__main__': main()
