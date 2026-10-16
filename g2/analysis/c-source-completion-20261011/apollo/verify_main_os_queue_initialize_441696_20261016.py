#!/usr/bin/env python3
"""Compare stock/C FreeRTOS queue initializer writes and reset call."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_queue_initialize_441696.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/Source/queue.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[1]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x441696-0x438000:0x4416b8-0x438000]
assert len(BODY) == 34

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) void audio_os_queue_reset_441516(uint32_t a,uint32_t b){__asm volatile("bx lr");}\n')
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_queue_initialize_441696',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, length, item_size, kind, seed):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        control, storage = 0x20000200, 0x20000400
        cpu.mem_write(control, bytes((seed + i) & 255 for i in range(80)))
        for reg, value in ((A.UC_ARM_REG_R0, length), (A.UC_ARM_REG_R1, item_size),
                           (A.UC_ARM_REG_R2, storage), (A.UC_ARM_REG_R3, kind),
                           (A.UC_ARM_REG_SP, 0x2000f000),
                           (A.UC_ARM_REG_LR, 0x600001)):
            cpu.reg_write(reg, value)
        cpu.mem_write(0x2000f000, control.to_bytes(4, 'little'))
        cut = (symbols['audio_os_queue_reset_441516'] & ~1) if compiled else 0x441516
        seen = []

        def lower(uc, address, size, _):
            if address != cut: return
            seen.append((uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1),
                         bytes(uc.mem_read(control, 80))))
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_os_queue_initialize_441696'] if compiled else 0x441696
        cpu.emu_start(entry | 1, 0x600000, count=100)
        return seen, bytes(cpu.mem_read(control, 80)), cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for length in (1, 7, 0xffffffff):
        for item_size in (0, 1, 8):
            for kind in (0, 4, 0x104):
                for seed in (0, 53):
                    stock = run(False, length, item_size, kind, seed)
                    candidate = run(True, length, item_size, kind, seed)
                    assert stock == candidate, (length, item_size, kind, seed, stock, candidate)
                    cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-queue-initialize-441696'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_QUEUE_INITIALIZE_441696', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'lower_boundary': {'audio_os_queue_reset_441516': '0x441516'},
           'limits': ['Queue reset remains a controlled lower call.',
                      'This does not prove final RTOS heap or physical operation.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
