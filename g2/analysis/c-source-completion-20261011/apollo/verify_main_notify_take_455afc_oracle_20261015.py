#!/usr/bin/env python3
"""Compare bounded FreeRTOS notification-take state and scheduler calls."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/task_notify_take_455afc.c'
OUT = G2 / 'build/c-firmware/20261015/main-notify-take-455afc'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
void *g2_audio_current_task;
__attribute__((noinline)) void audio_delay_scheduler_assert(void) {}
__attribute__((noinline)) void stock_enter_critical(void) {}
__attribute__((noinline)) void stock_exit_critical(void) {}
__attribute__((noinline)) void audio_add_current_to_delayed(uint32_t a,uint32_t b) {(void)a;(void)b;}
__attribute__((noinline)) void audio_yield(void) {}
'''
NATIVE = {'enter': 0x4420d0, 'exit': 0x4420e8,
          'delay': 0x455fa8, 'yield': 0x4420bc}


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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_notify_take_455afc',
                        str(SRC), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, value, clear, ticks):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            task = 0x20010000
            cpu.mem_write(task, bytes(0x100))
            cpu.mem_write(task + 0x68, value.to_bytes(4, 'little'))
            current = syms['g2_audio_current_task'] if compiled else 0x20074a20
            cpu.mem_write(current, task.to_bytes(4, 'little'))
            targets = ({key: syms[{'enter': 'stock_enter_critical',
                                   'exit': 'stock_exit_critical',
                                   'delay': 'audio_add_current_to_delayed',
                                   'yield': 'audio_yield'}[key]] & ~1
                        for key in NATIVE} if compiled else NATIVE)
            reverse = {address: name for name, address in targets.items()}
            trace = []

            def hook(cpu, address, size, _):
                name = reverse.get(address)
                if name is None:
                    return
                args = ((cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1))
                        if name == 'delay' else ())
                trace.append((name, *args))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_R1, clear)
            cpu.reg_write(A.UC_ARM_REG_R2, ticks)
            start = syms['audio_uart_notify_take_455afc'] if compiled else 0x455afc
            cpu.emu_start(start | 1, 0x600000, count=10000)
            return cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(task + 0x68, 5)), trace

        count = 0
        for value, clear, ticks in itertools.product(
                (0, 1, 2, 0xffffffff), (0, 1), (0, 1, 0xffffffff)):
            native = run(False, value, clear, ticks)
            source = run(True, value, clear, ticks)
            if native != source:
                raise AssertionError((value, clear, ticks, native, source))
            count += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_NOTIFY_TAKE_ORACLE',
               'cases': count, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'scope': 'index zero, 24 value/clear/wait combinations; scheduler children stubbed',
               'hardware_proof': False}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count)


if __name__ == '__main__':
    main()
