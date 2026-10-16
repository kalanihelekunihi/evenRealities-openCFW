#!/usr/bin/env python3
"""Compare stock/C system-close registry command, state and app gate."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/system_close_common_data_469d48.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-system-close-common-data-469d48'
HOOKS = {'audio_uart_device_role_get': 0x45a568,
         'audio_log_wake_allowed': 0x443484,
         'audio_system_close_active_app_get_443504': 0x443504,
         'audio_system_alert_command_45a8ee': 0x45a8ee,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n' + ''.join(
            f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
            for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_registry_callback_469d48',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, length, role, awake, app, status, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            selected = symbols['audio_system_close_selected_20075026'] if compiled else 0x20075026
            word = symbols['audio_system_close_payload_20074a04'] if compiled else 0x20074a04
            uc.mem_write(selected, b'\x5a'); uc.mem_write(word, b'\xa1\xa2\xa3\xa4')
            uc.mem_write(0x20021000, b'\x03\x12\x34\x56\x78\x9a')
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            for reg, val in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                 A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                (0x75, 0x20021000, length, 0x9999)):
                uc.reg_write(reg, val)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def read_string(cpu, ptr):
                return bytes(cpu.mem_read(ptr, 110)).split(b'\0', 1)[0].decode('ascii')
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                result = 0
                if name == 'audio_uart_device_role_get':
                    trace.append(('role',)); result = role
                elif name == 'audio_log_wake_allowed':
                    trace.append(('awake',)); result = awake
                elif name == 'audio_system_close_active_app_get_443504':
                    trace.append(('app-get',))
                    cpu.mem_write(r0, app.to_bytes(4, 'little'))
                    cpu.mem_write(r1, status.to_bytes(4, 'little'))
                elif name == 'audio_system_alert_command_45a8ee':
                    trace.append(('command', r0, r1, r2, r3))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    line = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                    fmt = int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')
                    trace.append(('extended', r0, line, read_string(cpu, fmt)))
                else:
                    trace.append(('short', r0, read_string(cpu, r1)))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_uart_registry_callback_469d48'] if compiled else 0x469d48
            uc.emu_start(start | 1, 0x600000, count=2000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return (uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(selected, 1)),
                    bytes(uc.mem_read(word, 4)), trace)
        cases = 0
        for length, role, awake, app, status, flags in itertools.product(
                (0, 4, 5, 6), (1, 2), (0, 1), (5, 8, 11, 14, 224, 4094),
                (0, 1), (0, 1, 2, 7)):
            args = (length, role, awake, app, status, flags)
            native, candidate = run(False, *args), run(True, *args)
            if native != candidate:
                raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_SYSTEM_CLOSE_COMMON_DATA_469D48',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x469d48-BASE:0x469e66-BASE]).hexdigest(),
                   'cases': cases,
                   'limits': ['Role, wake gate, active-app getter, display command and logging are controlled hooks; source-owned state spans are bounded to observed writes.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
