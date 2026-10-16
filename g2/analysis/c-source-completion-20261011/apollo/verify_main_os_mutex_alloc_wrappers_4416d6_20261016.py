#!/usr/bin/env python3
"""Stock/C call and return comparison of two RTOS mutex allocation wrappers."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_mutex_alloc_wrappers_4416d6.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODIES = {'audio_os_mutex_alloc_dynamic_4416d6': (0x4416d6, 0x4416f0),
          'audio_os_mutex_alloc_static_4416f0': (0x4416f0, 0x441710)}
LOWER = {'audio_os_mutex_dynamic_core_441636': 0x441636,
         'audio_os_mutex_static_core_4415ca': 0x4415ca,
         'audio_os_mutex_register_4416b8': 0x4416b8}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n' + '\n'.join(
        f'__attribute__((naked)) uint32_t {name}(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e)'
        '{__asm volatile("bx lr");}' for name in LOWER))
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_mutex_alloc_dynamic_4416d6',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, name, kind, memory, allocated):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.reg_write(A.UC_ARM_REG_R0, kind)
        cpu.reg_write(A.UC_ARM_REG_R1, memory)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[n] & ~1) if compiled else addr): n
                 for n, addr in LOWER.items()}
        trace = []

        def lower(uc, address, size, _):
            operation = hooks.get(address)
            if operation is None: return
            r0, r1, r2, r3 = (uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if operation.endswith('441636'):
                trace.append((operation, r0, r1, r2))
            elif operation.endswith('4415ca'):
                fifth = int.from_bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_SP), 4), 'little')
                trace.append((operation, r0, r1, r2, r3, fifth))
            else:
                trace.append((operation, r0))
            uc.reg_write(A.UC_ARM_REG_R0, allocated if operation !=
                         'audio_os_mutex_register_4416b8' else 0xdeadbeef)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols[name] if compiled else BODIES[name][0]
        cpu.emu_start(entry | 1, 0x600000, count=120)
        result = (cpu.reg_read(A.UC_ARM_REG_R0),)
        if name.endswith('4416f0'):
            result += (cpu.reg_read(A.UC_ARM_REG_R1),)
        return trace, result

    cases = 0
    for name in BODIES:
        for kind in (0, 1, 4, 0x101, 0xffffffff):
            for memory in (0, 0x20000200):
                for allocated in (0, 0x20001234):
                    stock = run(False, name, kind, memory, allocated)
                    candidate = run(True, name, kind, memory, allocated)
                    assert stock == candidate, (name, kind, memory, allocated, stock, candidate)
                    cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-mutex-alloc-wrappers-4416d6'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_MUTEX_ALLOC_WRAPPERS_4416D6',
           'cases': cases, 'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': {name: hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest()
                                  for name, (start, end) in BODIES.items()},
           'lower_boundary': LOWER,
           'limits': ['RTOS core allocation and registration remain controlled lower calls.',
                      'These cases do not establish heap or scheduler behavior.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
