#!/usr/bin/env python3
"""Compare stock/C FreeRTOS queue reset writes and lower-call order."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_queue_reset_441516.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/Source/queue.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[1]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x441516-0x438000:0x4415ca-0x438000]
assert len(BODY) == 180
LOWER = {'audio_os_interrupt_mask_5fa0a4': 0x5fa0a4,
         'stock_enter_critical': 0x4420d0,
         'stock_exit_critical': 0x4420e8,
         'audio_os_list_initialize_45607c': 0x45607c,
         'opencfw_ready_remove_event_list': 0x455370,
         'audio_yield': 0x4420bc}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n' + '\n'.join(
        f'__attribute__((naked)) uint32_t {name}(uint32_t a,uint32_t b)'
        '{__asm volatile("bx lr");}' for name in LOWER))
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_queue_reset_441516',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, present, length, item_size, new_queue, waiting, removed):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        queue = 0x20000200
        data = bytearray((7 + i) & 255 for i in range(80))
        for offset, value in ((0, 0x20000400), (16, waiting),
                              (60, length), (64, item_size)):
            data[offset:offset+4] = value.to_bytes(4, 'little')
        cpu.mem_write(queue, bytes(data))
        cpu.reg_write(A.UC_ARM_REG_R0, queue if present else 0)
        cpu.reg_write(A.UC_ARM_REG_R1, new_queue)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[name] & ~1) if compiled else address): name
                 for name, address in LOWER.items()}
        trace = []

        def lower(uc, address, size, _):
            name = hooks.get(address)
            if name is None: return
            args = (uc.reg_read(A.UC_ARM_REG_R0),) if name.endswith(
                ('45607c', '455370')) else ()
            trace.append((name,) + args)
            if name.endswith('5fa0a4'):
                uc.emu_stop()
                return
            uc.reg_write(A.UC_ARM_REG_R0, removed if name.endswith('455370') else 0)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_os_queue_reset_441516'] if compiled else 0x441516
        cpu.emu_start(entry | 1, 0x600000, count=300)
        failed = bool(trace and trace[-1][0].endswith('5fa0a4'))
        return trace, bytes(cpu.mem_read(queue, 80)), None if failed else cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for present in (False, True):
        for length, item_size in ((0, 0), (1, 0), (1, 3),
                                  (4, 3), (0xffffffff, 2)):
            for new_queue in (0, 1):
                for waiting in (0, 2):
                    for removed in (0, 1):
                        stock = run(False, present, length, item_size, new_queue,
                                    waiting, removed)
                        candidate = run(True, present, length, item_size, new_queue,
                                        waiting, removed)
                        assert stock == candidate, (present, length, item_size,
                                                    new_queue, waiting, removed,
                                                    stock, candidate)
                        cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-queue-reset-441516'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_QUEUE_RESET_441516', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'lower_boundary': LOWER,
           'limits': ['Invalid cases stop at the native interrupt-mask call before the deliberate fault.',
                      'Critical section, list, event and yield calls remain controlled boundaries.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
