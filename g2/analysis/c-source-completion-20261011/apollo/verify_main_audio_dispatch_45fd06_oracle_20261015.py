#!/usr/bin/env python3
"""Compare Apollo audio event dispatch and ring state with stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_dispatch_45fd06.c'
RING = G2 / 'components/audio/uart_thread_source_candidate/display_audio_event_ring_45fbba.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-dispatch-45fd06'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {
    'active': (0x45fcb2, 'audio_uart_display_audio_is_active_45fcb2'),
    'queue': (0x45f58c, 'audio_uart_display_audio_queue_45f58c'),
    'activate': (0x45f60e, 'audio_uart_display_audio_activate_45f60e'),
    'current': (0x45f8e6, 'audio_uart_display_audio_current_45f8e6'),
    'find': (0x45f840, 'audio_uart_display_audio_find_45f840'),
    'complete': (0x45f73a, 'audio_uart_display_audio_complete_45f73a'),
}
SHIM = '#include <stdint.h>\n' + '\n'.join(
    f'__attribute__((noinline)) uint32_t {name}(uint32_t a,uint32_t b)'
    '{(void)a;(void)b;return 0;}' for _, name in CALLS.values()) + '\n'

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_audio_dispatch_45fd06',
                        str(SRC), str(RING), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, state_valid, code, flagged, payload_valid,
                active_before, found, mode, action_active):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            state, entry = 0x20011000, 0x20012000
            cpu.mem_write(state, bytes(256))
            cpu.mem_write(entry, bytes(64))
            put(cpu, state + 36, code)
            put(cpu, state + 40, 0x42 if payload_valid else 0)
            cpu.mem_write(state + 44, bytes([flagged]))
            cpu.mem_write(state + 36 + 194, b'\x01')
            put(cpu, entry, 0x43)
            cpu.mem_write(entry + 11, bytes([mode]))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            widths = {'active': 1, 'current': 1, 'find': 2,
                      'queue': 2, 'activate': 2, 'complete': 2}
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1)
            trace = []
            active = bool(active_before)
            def hook(cpu, address, size, _):
                nonlocal active
                key = targets.get(address)
                if key is None:
                    return
                trace.append((key, tuple(cpu.reg_read(r) for r in regs[:widths[key]])))
                if key == 'active': result = int(active)
                elif key in ('current', 'find'): result = entry if found else 0
                else:
                    if key in ('queue', 'activate', 'complete'):
                        active = bool(action_active)
                    result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, state if state_valid else 0)
            start = syms['audio_uart_display_audio_dispatch_45fd06'] if compiled else 0x45fd06
            cpu.emu_start(start | 1, 0x600000, count=500)
            return trace, bytes(cpu.mem_read(state, 232))

        cases = 0
        for args in itertools.product((False, True), (0x3c, 0x3d, 0x3e, 0x40),
                                      (0, 1), (False, True), (False, True),
                                      (False, True), (0, 1), (False, True)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'dispatch mismatch {args}: {stock[0]} != {rebuilt[0]}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_DISPATCH_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'ring_source_sha256': hashlib.sha256(RING.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Ring transitions run; application action helpers are hooked.',
                          'Live callback effects and concurrency remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
