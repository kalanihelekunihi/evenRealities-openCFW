#!/usr/bin/env python3
"""Compare bounded page-manager audio event callback branches to Apollo."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_event_45f914.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-event-45f914'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'code': (0x450286, 'audio_uart_page_event_code_450286'),
    'active': (0x45fcb2, 'audio_uart_display_audio_is_active_45fcb2'),
    'gate': (0x45fbe6, 'audio_uart_display_audio_gate_event_45fbe6'),
    'queue': (0x45f58c, 'audio_uart_display_audio_queue_45f58c'),
    'current': (0x45f8e6, 'audio_uart_display_audio_current_45f8e6'),
    'activate': (0x45f60e, 'audio_uart_display_audio_activate_45f60e'),
    'find': (0x45f840, 'audio_uart_display_audio_find_45f840'),
    'complete': (0x45f73a, 'audio_uart_display_audio_complete_45f73a'),
    'handler_a': (0x45f6a8, 'audio_uart_display_audio_handler_a_45f6a8'),
    'handler_b': (0x45f66a, 'audio_uart_display_audio_handler_b_45f66a'),
    'level': (0x43d0ce, 'audio_log_level'),
    'extended': (0x43d574, 'audio_log_extended'),
    'compact': (0x43ce9e, 'compressed_log_output'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)'
    '{(void)a;(void)b;(void)c;(void)d;return 0;}'
    for _, name in CALLS.values()) + '\n'


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_page_event_45f914',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, code, active_byte, active_result, gate_result,
                param, id_value, entry_live, log_flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            event, page, parameter, current, found, handler_a, handler_b = (
                0x20011000, 0x20012000, 0x20013000, 0x20014000,
                0x20015000, 0x20016000, 0x20017000)
            for address, length in ((event, 0x100), (page, 0x200),
                                    (parameter, 0x100), (current, 0x100),
                                    (found, 0x100), (handler_a, 0x100),
                                    (handler_b, 0x100)):
                cpu.mem_write(address, bytes(length))
            put(cpu, event + 12, page)
            put(cpu, event + 16, parameter if param else 0)
            put(cpu, parameter, id_value)
            put(cpu, current, 0x12345678)
            put(cpu, found, id_value)
            cpu.mem_write(found + 11, bytes([1 if entry_live else 0]))
            for address in (current, handler_a, handler_b):
                put(cpu, address + 24, 0x2001f001)
            cpu.mem_write(page + 0xe8, bytes([active_byte]))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            trace = []

            def hook(cpu, address, size, _):
                if address == 0x2001f000:
                    trace.append(('callback', cpu.reg_read(A.UC_ARM_REG_R0),
                                  cpu.reg_read(A.UC_ARM_REG_R1),
                                  cpu.reg_read(A.UC_ARM_REG_R2),
                                  cpu.reg_read(A.UC_ARM_REG_R3)))
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                    return
                key = targets.get(address)
                if key is None:
                    return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if key in ('queue', 'activate', 'complete', 'gate', 'find'):
                    trace.append((key, r0, r1))
                elif key in ('extended', 'compact'):
                    trace.append((key, r0))
                else:
                    trace.append((key, r0 if key != 'level' else 0))
                result = {'code': code, 'active': active_result,
                          'gate': gate_result, 'current': current,
                          'find': found, 'handler_a': handler_a,
                          'handler_b': handler_b, 'level': log_flags}.get(key, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, event)
            entry = syms['audio_uart_page_event_45f914'] if compiled else 0x45f914
            cpu.emu_start(entry | 1, 0x600000, count=10000)
            return trace, bytes(cpu.mem_read(page, 0xf0))

        cases = list(itertools.product((0x3c, 0x3d, 0x3e, 0x40, 0x41),
                                       (0, 1), (0, 1), (0, 1),
                                       (False, True), (0, 0x1234),
                                       (False, True), (0,)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[0], source[0]))
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_EVENT_ORACLE',
               'cases': len(cases), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'official_payload_sha256': digest,
               'scope': 'five event codes, active/gate/parameter/entry branches; controlled children',
               'hardware_proof': False}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases))


if __name__ == '__main__': main()
