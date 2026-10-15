#!/usr/bin/env python3
"""Bounded native/C running app ID parity with logging disabled."""
from pathlib import Path
import hashlib, json, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/terminal-running-apps-round992'
out.mkdir(parents=True, exist_ok=True)
src = root / 'components/audio/uart_thread_source_candidate/terminal_running_app_ids.c'
base = root / 'build/c-firmware/terminal-division-bridge-round991/apollo-main-terminal-division-bridge.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj = out / 'terminal_running_app_ids.o'
linked = out / 'apollo-main-terminal-running-apps.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-fshort-enums', '-fno-builtin', '-O2', '-Wall', '-Wextra', '-Werror',
                '-c', str(src), '-o', str(obj)], check=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('#include <stdint.h>\nuint8_t audio_uart_display_state[2];uint32_t audio_uart_display_mode,audio_uart_display_active,audio_uart_display_background;\nuint32_t audio_log_flags(void){return 0;}\nvoid audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\nuint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_get_running_app_ids', str(src), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        syms = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    cases = 0
    for state in (0, 1, 2):
        for mode in (0, 1, 2, 3):
            for null in (0, 1, 2):
             for log_flags in (0, 1, 2, 4):
                pair = []
                for compiled in (False, True):
                    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                    u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
                    u.mem_map(0x100000, 0x100000)
                    for addr, data in segs: u.mem_write(addr, data)
                    u.mem_map(0x20000000, 0x200000)
                    cells = {'audio_uart_display_state': 0x20074f2c,
                             'audio_uart_display_mode': 0x200744dc,
                             'audio_uart_display_active': 0x200744d8,
                             'audio_uart_display_background': 0x200744e0}
                    def cell(name): return syms[name] if compiled else cells[name]
                    u.mem_write(cell('audio_uart_display_state'), bytes([state]))
                    u.mem_write(cell('audio_uart_display_mode'), mode.to_bytes(4, 'little'))
                    u.mem_write(cell('audio_uart_display_active'), (0x12345678).to_bytes(4, 'little'))
                    u.mem_write(cell('audio_uart_display_background'), (0xabcdef01).to_bytes(4, 'little'))
                    traces = []
                    hooks = {'flags': syms['audio_log_flags'] if compiled else 0x43d0ce,
                             'extended': syms['audio_log_extended'] if compiled else 0x43d574,
                             'compact': syms['compressed_log_output'] if compiled else 0x43ce9e}
                    for kind, address in hooks.items():
                        def hook(cpu, at, size, user, kind=kind):
                            if kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0, log_flags)
                            else: traces.append((kind, cpu.reg_read(A.UC_ARM_REG_R0)))
                            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE, hook, begin=address & ~1, end=address & ~1)
                    x, y = 0x2001f000, 0x2001f004
                    u.mem_write(x, b'\xaa' * 8)
                    u.reg_write(A.UC_ARM_REG_R0, 0 if null == 1 else x)
                    u.reg_write(A.UC_ARM_REG_R1, 0 if null == 2 else y)
                    u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
                    u.reg_write(A.UC_ARM_REG_LR, 0x600001)
                    u.emu_start((syms['audio_get_running_app_ids'] if compiled else 0x443504) | 1,
                                0x600000, count=500)
                    pair.append((u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(x, 8)), traces))
                assert pair[0] == pair[1], (state, mode, null, log_flags, pair)
                cases += 1
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}
before, after = imports(base), imports(linked)
assert before - after == {'audio_get_running_app_ids'} and not after - before
receipt = {'round': 992, 'status': 'PASS_TERMINAL_RUNNING_APP_IDS_LOG_CLASSES',
           'component': 'Apollo running app ID provider 0x443504',
           'source': str(src.relative_to(root)),
           'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
           'official_image_sha256': hashlib.sha256(blob).hexdigest(),
           'cases': cases, 'validation': 'M55 strict compile and native/C ID, return and logging call-class parity for flags 0,1,2,4',
           'linked_object': str(linked.relative_to(root)),
           'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
           'unresolved_before': len(before), 'unresolved_after': len(after),
           'whole_image_complete': False, 'hardware_proof': False,
           'gates': ['Logging payload and unconstrained entry R3 in mode 1 remain unverified',
                     'Full image layout and hardware proof remain open']}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, len(before), len(after), receipt['linked_sha256'])
