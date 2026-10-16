#!/usr/bin/env python3
"""Compare Apollo animation finish callback with pinned stock Thumb."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_anim_finish_c_45ecca.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-anim-finish-c-45ecca'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS = {'owner': (0x45fcd2, 'audio_uart_display_audio_find_owner_45fcd2'),
         'finalize': (0x45bbd2, 'audio_uart_display_audio_finalize'),
         'dispatch': (0x45fd06, 'audio_uart_display_audio_dispatch_45fd06'),
         'log_level': (0x43d0ce, 'audio_log_level'),
         'log_extended': (0x43d574, 'audio_log_extended'),
         'log_compact': (0x43ce9e, 'compressed_log_output')}
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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_display_anim_finish_c_45eccb',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, owner_valid, callback_valid, flag, owner_flag, log_mask):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            desc, page, entry, owner = 0x20011000, 0x20012000, 0x20013000, 0x20014000
            for address in (desc, page, entry, owner):
                cpu.mem_write(address, bytes(256))
            put(cpu, desc, page)
            put(cpu, page + 16, entry)
            put(cpu, entry + 24, 0x20018001 if callback_valid else 0)
            cpu.mem_write(entry + 28, bytes([flag]))
            cpu.mem_write(owner + 232, bytes([owner_flag]))
            targets = {(syms[name] if compiled else address) & ~1: key
                       for key, (address, name) in CALLS.items()}
            targets[0x20018000] = 'callback'
            widths = {'owner': 1, 'finalize': 0, 'dispatch': 1, 'callback': 4,
                      'log_level': 0}
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            trace = []
            def cstring(ptr):
                data = bytes(cpu.mem_read(ptr, 128))
                return data.split(b'\x00', 1)[0].decode('utf-8')
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                values = tuple(cpu.reg_read(r) for r in regs)
                if key == 'log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    line = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                    message_ptr = int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')
                    trace.append((key, values[0], *(cstring(v) for v in values[1:]),
                                  line, cstring(message_ptr)))
                elif key == 'log_compact':
                    trace.append((key, values[0], cstring(values[1]), cstring(values[2])))
                else:
                    trace.append((key, values[:widths[key]]))
                cpu.reg_write(A.UC_ARM_REG_R0,
                              owner if key == 'owner' and owner_valid else
                              log_mask if key == 'log_level' else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, desc)
            start = syms['audio_uart_display_anim_finish_c_45eccb'] if compiled else 0x45ecca
            cpu.emu_start(start | 1, 0x600000, count=200)
            return trace, bytes(cpu.mem_read(entry + 28, 1)), bytes(cpu.mem_read(owner + 232, 1))

        cases = 0
        for args in itertools.product((False, True), (False, True),
                                      (0, 2), (0, 1), (0, 1, 2, 4, 7)):
            stock, rebuilt = run(False, *args), run(True, *args)
            if stock != rebuilt:
                raise RuntimeError(f'finish mismatch {args}: {stock} != {rebuilt}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ANIM_FINISH_C_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Owner, callback, finalize and dispatch calls are hooked.',
                          'Logging branches compare format strings and call arguments.',
                          'Live callback effects remain open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
