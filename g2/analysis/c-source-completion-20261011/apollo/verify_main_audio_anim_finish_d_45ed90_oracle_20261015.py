#!/usr/bin/env python3
"""Compare Apollo animation finish D against the pinned stock Thumb body."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_anim_finish_d_45ed90.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-anim-finish-d-45ed90'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'finalize': (0x45bbd2, 'audio_uart_display_audio_finalize'),
         'parent': (0x44dca2, 'audio_uart_lv_obj_parent_44dca2'),
         'queue': (0x45f58c, 'audio_uart_display_audio_queue_45f58c'),
         'dispatch': (0x45fd06, 'audio_uart_display_audio_dispatch_45fd06')}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(uint32_t a)'
    '{(void)a;return 0;}' for _, name in CALLS.values()) + '\n'

def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_anim_finish_d_45ed91',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, chain, queued, ready, current_callback, entry_callback):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            desc, page, entry, parent1, parent2, owner, current = (
                0x20011000, 0x20012000, 0x20013000, 0x20014000,
                0x20015000, 0x20016000, 0x20017000)
            for address in (desc, page, entry, parent1, parent2, owner, current):
                cpu.mem_write(address, bytes(256))
            put(cpu, desc, page)
            put(cpu, page + 16, entry)
            put(cpu, parent1 + 16, 0 if chain else owner)
            put(cpu, parent2 + 16, owner)
            put(cpu, owner + 16, 0x20019000 if queued else 0)
            put(cpu, owner + 12, current)
            put(cpu, owner + 4, 0x12345678)
            cpu.mem_write(owner + 20, b'\x05')
            cpu.mem_write(owner + 232, b'\x07')
            cpu.mem_write(entry + 28, b'\x09')
            put(cpu, entry + 24, 0x2001a001 if entry_callback else 0)
            cpu.mem_write(current + 28, bytes([1 if ready else 0]))
            put(cpu, current + 24, 0x2001b001 if current_callback else 0)
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            targets[0x2001a000] = 'entry_callback'
            targets[0x2001b000] = 'current_callback'
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            trace = []
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                values = tuple(cpu.reg_read(r) for r in regs)
                width = 0 if key == 'finalize' else 4 if key.endswith('callback') else 1
                trace.append((key, values[:width]))
                result = (parent1 if values[0] == page else parent2) if key == 'parent' else 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, desc)
            start = syms['audio_uart_display_anim_finish_d_45ed91'] if compiled else 0x45ed90
            cpu.emu_start(start | 1, 0x600000, count=400)
            state = (bytes(cpu.mem_read(entry + 28, 1)),
                     bytes(cpu.mem_read(owner + 4, 4)),
                     bytes(cpu.mem_read(owner + 16, 4)),
                     bytes(cpu.mem_read(owner + 20, 1)),
                     bytes(cpu.mem_read(owner + 232, 1)))
            return trace, state

        cases = 0
        for args in itertools.product((False, True), repeat=5):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'finish D mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ANIM_FINISH_D_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Parent, finalize, queue, dispatch and callback calls are hooked.',
                          '32 controlled parent, queue, ready and callback combinations.',
                          'Live animation and queue effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
