#!/usr/bin/env python3
"""Compare stock/C FreeRTOS queue create paths at controlled lower boundaries."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_queue_create_cores_4415ca.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/Source/queue.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[1]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODIES = {'audio_os_mutex_static_core_4415ca': (0x4415ca, 0x441636),
          'audio_os_mutex_dynamic_core_441636': (0x441636, 0x441696)}
LOWER = {'audio_os_interrupt_mask_5fa0a4': 0x5fa0a4,
         'pvPortMalloc': 0x456110,
         'audio_os_queue_initialize_441696': 0x441696}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n' + '\n'.join(
        f'__attribute__((naked)) uint32_t {name}(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e)'
        '{__asm volatile("bx lr");}' for name in LOWER))
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_mutex_static_core_4415ca',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, name, length, item_size, storage, control, kind, allocated):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        cell = 0x20000200
        cpu.mem_write(cell, bytes(range(80)))
        args = (length, item_size, storage, control, kind) if name.endswith('4415ca') else \
               (length, item_size, kind, 0, 0)
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), args[:4]):
            cpu.reg_write(reg, value)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.mem_write(0x2000f000, args[4].to_bytes(4, 'little'))
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[n] & ~1) if compiled else address): n
                 for n, address in LOWER.items()}
        trace = []

        def lower(uc, address, size, _):
            op = hooks.get(address)
            if op is None: return
            r0, r1, r2, r3 = (uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if op.endswith('5fa0a4'):
                trace.append((op,))
                uc.emu_stop()
                return
            if op == 'pvPortMalloc':
                trace.append((op, r0))
                uc.reg_write(A.UC_ARM_REG_R0, allocated)
            else:
                fifth = int.from_bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_SP), 4), 'little')
                trace.append((op, r0, r1, r2, r3, fifth))
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols[name] if compiled else BODIES[name][0]
        cpu.emu_start(entry | 1, 0x600000, count=300)
        failed = bool(trace and trace[-1][0].endswith('5fa0a4'))
        return trace, bytes(cpu.mem_read(cell, 80)), None if failed else cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for kind in (0, 4, 0x104):
        for length, item_size, storage, control in (
            (1, 0, 0, 0x20000200), (2, 3, 0x20000300, 0x20000200),
            (0, 0, 0, 0x20000200), (1, 0, 0x20000300, 0x20000200),
            (1, 3, 0, 0x20000200), (1, 0, 0, 0),
            (0xffffffff, 2, 0, 0x20000200), (1, 0xffffffff, 0, 0x20000200)):
            for allocated in (0, 0x20000200):
                for name in BODIES:
                    stock = run(False, name, length, item_size, storage, control, kind, allocated)
                    candidate = run(True, name, length, item_size, storage, control, kind, allocated)
                    assert stock == candidate, (name, length, item_size, storage,
                                                control, kind, allocated, stock, candidate)
                    cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-queue-create-cores-4415ca'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_QUEUE_CREATE_CORES_4415CA',
           'cases': cases, 'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': {name: hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest()
                                  for name, (start, end) in BODIES.items()},
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'lower_boundary': LOWER,
           'limits': ['Invalid inputs stop at the native interrupt-mask call before the deliberate fault.',
                      'Heap allocation and shared queue initialization remain controlled lower calls.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
