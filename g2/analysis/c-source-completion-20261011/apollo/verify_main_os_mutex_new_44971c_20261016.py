#!/usr/bin/env python3
"""Stock/C lower-call and result comparison for CMSIS osMutexNew."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_mutex_new_44971c.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[4]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
upstream_text = UPSTREAM.read_text()
assert 'osMutexId_t osMutexNew (const osMutexAttr_t *attr)' in upstream_text
assert 'attr->cb_size >= sizeof(StaticSemaphore_t)' in upstream_text
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x44971c-0x438000:0x4497b6-0x438000]
assert len(BODY) == 154
LOWER = {'audio_os_irq_context_44900e': 0x44900e,
         'audio_os_mutex_alloc_dynamic_4416d6': 0x4416d6,
         'audio_os_mutex_alloc_static_4416f0': 0x4416f0}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n' + '\n'.join(
        f'__attribute__((naked)) uint32_t {name}(uint32_t a,uint32_t b)'
        '{__asm volatile("bx lr");}' for name in LOWER))
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_even_ai_mutex_create_44971c',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, use_attr, flags, memory, size, irq, allocated):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        attr = 0x20000100 if use_attr else 0
        if attr:
            cpu.mem_write(attr, b''.join(x.to_bytes(4, 'little') for x in
                                      (0, flags, memory, size)))
        cpu.reg_write(A.UC_ARM_REG_R0, attr)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[name] & ~1) if compiled else address): name
                 for name, address in LOWER.items()}
        trace = []

        def lower(uc, address, size, _):
            name = hooks.get(address)
            if name is None: return
            args = tuple(uc.reg_read(reg) for reg in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1))
            trace.append((name,) + (() if name.endswith('44900e') else
                                    args[:1] if name.endswith('4416d6') else args))
            uc.reg_write(A.UC_ARM_REG_R0, irq if name.endswith('44900e') else allocated)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_even_ai_mutex_create_44971c'] if compiled else 0x44971c
        cpu.emu_start(entry | 1, 0x600000, count=250)
        return trace, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for use_attr in (False, True):
        for flags in (0, 1, 8, 9):
            for memory, size in ((0, 0), (0, 80), (0x20000200, 79), (0x20000200, 80)):
                for irq in (0, 1):
                    for allocated in (0, 0x20001234):
                        stock = run(False, use_attr, flags, memory, size, irq, allocated)
                        candidate = run(True, use_attr, flags, memory, size, irq, allocated)
                        assert stock == candidate, (use_attr, flags, memory, size, irq,
                                                    allocated, stock, candidate)
                        cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-mutex-new-44971c'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_MUTEX_NEW_44971C', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'lower_boundary': LOWER,
           'limits': ['IRQ context and allocator bodies are controlled lower calls.',
                      'These cases do not establish RTOS timing or physical mutex behavior.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
