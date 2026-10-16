#!/usr/bin/env python3
"""Compare three Apollo audio animation value callbacks with stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_anim_setters_45ecae.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-anim-setters-45ecae'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CASES = {'x': (0x45ecae, 'audio_uart_display_anim_x_a_45ecaf',
               0x43f0e0, 'audio_uart_page_43f0e0'),
         'y': (0x45ecb6, 'audio_uart_display_anim_y_a_45ecb7',
               0x43f142, 'audio_uart_page_43f142'),
         'alpha': (0x45ecbe, 'audio_uart_display_anim_alpha_45ecbf',
                   0x441488, 'audio_uart_display_audio_reset_441488')}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) void {name}(uint32_t a,uint32_t b,uint32_t c)'
    '{(void)a;(void)b;(void)c;}' for name in [c[3] for c in CASES.values()]) + '\n'

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_anim_x_a_45ecaf',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, kind, object, value):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            source_addr, source_name, child_addr, child_name = CASES[kind]
            target = (syms[child_name] if compiled else child_addr) & ~1
            trace = []
            def hook(cpu, address, size, _):
                if address != target:
                    return
                regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)
                trace.append(tuple(cpu.reg_read(r) for r in regs[:3 if kind == 'alpha' else 2]))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, object)
            cpu.reg_write(A.UC_ARM_REG_R1, value)
            start = syms[source_name] if compiled else source_addr
            cpu.emu_start(start | 1, 0x600000, count=100)
            return trace

        cases = 0
        for kind, object, value in itertools.product(
                CASES, (0, 0x20012000), (0, 1, 0xff, 0x100, 0xffffffff)):
            stock, rebuilt = run(False, kind, object, value), run(True, kind, object, value)
            if stock != rebuilt:
                raise RuntimeError(f'animation setter mismatch {kind=} {object=} {value=}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ANIM_SETTERS_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Child setter effects are hooked; call arguments are native compared.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
