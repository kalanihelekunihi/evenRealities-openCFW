#!/usr/bin/env python3
"""Compare Apollo mutex registration writes and lower call with stock."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_mutex_register_4416b8.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x4416b8-0x438000:0x4416d6-0x438000]
assert len(BODY) == 30

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) void audio_uart_queue_send(uint32_t a,uint32_t b,uint32_t c,uint32_t d){__asm volatile("bx lr");}\n')
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_mutex_register_4416b8',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, mutex, seed):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        cell = 0x20000200
        initial = bytes((seed + index) & 255 for index in range(20))
        cpu.mem_write(cell, initial)
        cpu.reg_write(A.UC_ARM_REG_R0, mutex)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cut = (symbols['audio_uart_queue_send'] & ~1) if compiled else 0x4417ee
        seen = []

        def lower(uc, address, size, _):
            if address != cut: return
            args = tuple(uc.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            seen.append(args)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_os_mutex_register_4416b8'] if compiled else 0x4416b8
        cpu.emu_start(entry | 1, 0x600000, count=100)
        return seen, bytes(cpu.mem_read(cell, 20))

    cases = 0
    for mutex in (0, 0x20000200):
        for seed in (0, 17, 255):
            stock = run(False, mutex, seed)
            candidate = run(True, mutex, seed)
            assert stock == candidate, (mutex, seed, stock, candidate)
            cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-mutex-register-4416b8'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_MUTEX_REGISTER_4416B8', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'lower_boundary': {'audio_uart_queue_send': '0x4417ee'},
           'limits': ['The mutex link helper remains a controlled lower call.',
                      'Six memory/call cases do not prove RTOS runtime behavior.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
