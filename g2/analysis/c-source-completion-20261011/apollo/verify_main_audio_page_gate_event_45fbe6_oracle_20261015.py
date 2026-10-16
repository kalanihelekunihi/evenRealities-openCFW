#!/usr/bin/env python3
"""Compare audio event ring enqueue with the pinned stock Main payload."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_gate_event_45fbe6.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-gate-event-45fbe6'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = ('#include <stdint.h>\n'
        '__attribute__((noinline)) uint32_t audio_uart_page_event_code_450286(const void*a)'
        '{(void)a;return 0;}\n')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_gate_event_45fbe6',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, event_valid, count, index, has_ptr, value):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, event, payload = 0x20011000, 0x20012000, 0x20013000
            cpu.mem_write(state, bytes(256))
            cpu.mem_write(event, bytes(64))
            cpu.mem_write(payload, value.to_bytes(4, 'little'))
            cpu.mem_write(state + 36 + 193, bytes([index]))
            cpu.mem_write(state + 36 + 194, bytes([count]))
            cpu.mem_write(event + 16, (payload if has_ptr else 0).to_bytes(4, 'little'))
            target = (syms['audio_uart_page_event_code_450286'] if compiled else 0x450286) & ~1
            calls = []
            def hook(cpu, address, size, _):
                if address != target:
                    return
                calls.append(cpu.reg_read(A.UC_ARM_REG_R0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x77)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if state_valid else 0)
            cpu.reg_write(A.UC_ARM_REG_R1, event if event_valid else 0)
            start = syms['audio_uart_display_audio_gate_event_45fbe6'] if compiled else 0x45fbe6
            cpu.emu_start(start | 1, 0x600000, count=300)
            return cpu.reg_read(A.UC_ARM_REG_R0), calls, bytes(cpu.mem_read(state, 256))

        cases = 0
        for args in itertools.product((False, True), (False, True), (0, 15, 16, 255),
                                      (0, 1, 15), (False, True), (0, 0x12345678)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'event ring mismatch {args}: {stock[:2]} != {rebuilt[:2]}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_GATE_EVENT_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA, 'stock_entry': '0x45fbe6',
               'limits': ['Event-code helper is hooked; ring dispatch is not exercised.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
