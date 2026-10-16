#!/usr/bin/env python3
"""Compare stock and C silent-mode application command routing."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/silent_mode_set_from_app_46921c.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x46921c-BASE:0x469388-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-silent-mode-set-from-app-46921c'
HOOKS = {'audio_silent_mode_status_get': 0x46919e,
         'audio_log_wake_allowed': 0x443484,
         'audio_uart_device_role_get': 0x45a568,
         'audio_uart_master_display_stop': 0x464c36,
         'audio_uart_task_delay': 0x454b4c,
         'audio_sync_send_to_both_ext_464f76': 0x464f76,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}
CELLS = {'audio_silent_mode_showing_ui_2007501f': 0x2007501f,
         'audio_silent_mode_change_from_app': 0x2007501e,
         'audio_uart_display_active': 0x200744d8,
         'audio_uart_display_mode': 0x200744dc,
         'audio_uart_display_background': 0x200744e0}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n' +
                        ''.join(f'uint32_t {name};\n' for name in CELLS if name != 'audio_silent_mode_showing_ui_2007501f') +
                        ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_silent_mode_set_from_app_46921c',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, showing, requested, current, wake, role, background,
                active, mode, send_result, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            vals = (showing, 0xa5, active, mode, background)
            for (name, address), val in zip(CELLS.items(), vals):
                location = symbols[name] if compiled else address
                uc.mem_write(location, bytes([val & 255]) if name.startswith('audio_silent_mode_') else u32(val))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000); uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, requested)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def observe(cpu, address, size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if name == 'audio_silent_mode_status_get':
                    trace.append(('status',)); result = current
                elif name == 'audio_log_wake_allowed':
                    trace.append(('wake',)); result = wake
                elif name == 'audio_uart_device_role_get':
                    trace.append(('role',)); result = role
                elif name == 'audio_uart_master_display_stop':
                    trace.append(('stop', r0, r1, r2, r3)); result = 0
                elif name == 'audio_uart_task_delay':
                    trace.append(('delay', r0)); result = 0
                elif name == 'audio_sync_send_to_both_ext_464f76':
                    value = int.from_bytes(cpu.mem_read(r1, 4), 'little')
                    arg5 = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP), 4), 'little')
                    trace.append(('send', r0, value, r2, r3, arg5))
                    result = send_result
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0)); result = 0
                else:
                    trace.append(('short', r0)); result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_silent_mode_set_from_app_46921c'] if compiled else 0x46921c
            uc.emu_start(start | 1, 0x600000, count=600)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            change = symbols['audio_silent_mode_change_from_app'] if compiled else CELLS['audio_silent_mode_change_from_app']
            return bytes(uc.mem_read(change, 1)), trace
        cases = 0
        for showing, requested, current, wake, role, screen, send_result, flags in itertools.product(
                (0, 1), (0, 1, 255), (0, 1), (0, 1), (0, 1),
                ((0, 0, 0), (1, 0, 0), (0, 1, 1), (1, 1, 1)), (0, 7), (0, 1, 2, 4, 7)):
            args = (showing, requested, current, wake, role, *screen, send_result, flags)
            native = run(False, *args); candidate = run(True, *args)
            if native != candidate: raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_SILENT_MODE_SET_FROM_APP_46921C',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Status, wake, role, display stop, delay, send-to-both and logging calls are controlled hooks; send-to-both implementation and hardware behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
