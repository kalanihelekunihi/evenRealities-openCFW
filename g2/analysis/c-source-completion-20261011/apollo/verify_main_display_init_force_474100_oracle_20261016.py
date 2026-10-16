#!/usr/bin/env python3
"""Compare stock and C display force-init queue/log behavior."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_init_force_474100.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x474100-BASE:0x4742f8-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-display-init-force-474100'
HOOKS = {'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e, 'audio_uart_buffer_zero': 0x43c0e4,
         'audio_cmsis_queue_put': 0x449abe, 'audio_log_wake_allowed': 0x443484}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n'
                        'volatile uint32_t audio_uart_display_manager_queue_cell;\n'
                        'uint32_t audio_display_hw_initialized_200744ec;\n' +
                        ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_wear_child_474100',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, initialized, wake, queue_results, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            state = symbols['audio_display_hw_initialized_200744ec'] if compiled else 0x200744ec
            queue_cell = symbols['audio_uart_display_manager_queue_cell'] if compiled else 0x20000664
            uc.mem_write(state, u32(initialized)); uc.mem_write(queue_cell, u32(0x12345678))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000); uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            queue_index = [0]
            def observe(cpu, address, size, _):
                name = hooks.get(address)
                if name is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                if name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_wake_allowed':
                    trace.append(('wake',)); result = wake
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0)); result = 0
                elif name == 'compressed_log_output':
                    trace.append(('short', r0)); result = 0
                elif name == 'audio_uart_buffer_zero':
                    length = cpu.reg_read(A.UC_ARM_REG_R1)
                    value = cpu.reg_read(A.UC_ARM_REG_R2) & 0xff
                    trace.append(('zero', length, value))
                    cpu.mem_write(r0, bytes([value]) * length); result = r0
                else:
                    ptr = cpu.reg_read(A.UC_ARM_REG_R1)
                    packet = tuple(int.from_bytes(cpu.mem_read(ptr + i * 4, 4), 'little') for i in range(9))
                    trace.append(('queue', r0, packet, cpu.reg_read(A.UC_ARM_REG_R2),
                                  cpu.reg_read(A.UC_ARM_REG_R3)))
                    result = queue_results[queue_index[0]]
                    queue_index[0] += 1
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_wear_child_474100'] if compiled else 0x474100
            uc.emu_start(start | 1, 0x600000, count=300)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return uc.reg_read(A.UC_ARM_REG_R0), trace
        cases = 0
        for initialized in (0, 1):
            for wake in (0, 1):
                for bits in range(8):
                    queue_results = tuple((bits >> i) & 1 for i in range(3))
                    for flags in (0, 1, 2, 4, 7):
                        args = (initialized, wake, queue_results, flags)
                        native = run(False, *args); candidate = run(True, *args)
                        if native != candidate: raise AssertionError((args, native, candidate))
                        cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_DISPLAY_INIT_FORCE_474100',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Wake predicate, queue, buffer-zero and logging calls are controlled hooks; final hardware-state and queue-cell placement and hardware behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
