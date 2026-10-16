#!/usr/bin/env python3
"""Stock/C comparison of the EvenAI lazy RAM-cell initializer."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/even_ai_prepare_4e1f7c.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x4e1f7c-0x438000:0x4e1fa6-0x438000]
assert len(BODY) == 42
LOWER = {'audio_even_ai_mutex_create_44971c': 0x44971c,
         'audio_os_interrupt_mask_5fa0a4': 0x5fa0a4}
CELL = 0x20074580

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) uint32_t audio_even_ai_mutex_create_44971c(uint32_t a){__asm volatile("bx lr");}\n'
                    '__attribute__((naked)) void audio_os_interrupt_mask_5fa0a4(void){__asm volatile("bx lr");}\n')
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_even_ai_prepare_4e1f7c',
                    '-Wl,--defsym=audio_even_ai_mutex_20074580=0x20074580',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, initial, created):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x80000)
        cpu.mem_write(CELL, initial.to_bytes(4, 'little'))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[name] & ~1) if compiled else address): name
                 for name, address in LOWER.items()}
        seen = []

        def lower(uc, address, size, _):
            name = hooks.get(address)
            if name is None: return
            seen.append((name, uc.reg_read(A.UC_ARM_REG_R0)) if
                        name.endswith('44971c') else (name,))
            if name.endswith('5fa0a4'):
                uc.emu_stop()
                return
            uc.reg_write(A.UC_ARM_REG_R0, created)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_even_ai_prepare_4e1f7c'] if compiled else 0x4e1f7c
        cpu.emu_start(entry | 1, 0x600000, count=150)
        value = int.from_bytes(cpu.mem_read(CELL, 4), 'little')
        return seen, value

    cases = 0
    for initial in (0, 0x12345678):
        for created in (0, 0x2000abcd):
            stock = run(False, initial, created)
            candidate = run(True, initial, created)
            assert stock == candidate, (initial, created, stock, candidate)
            cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-even-ai-prepare-4e1f7c'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_EVEN_AI_PREPARE_4E1F7C', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'ram_cell': hex(CELL), 'lower_boundary': LOWER,
           'limits': ['Failure cases stop at the native interrupt-mask call before the deliberate fault.',
                      'RAM initialization, allocation extent and placement remain unqualified.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
