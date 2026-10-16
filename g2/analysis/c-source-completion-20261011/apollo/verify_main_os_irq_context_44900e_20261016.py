#!/usr/bin/env python3
"""Stock/C Cortex-M IRQ-context and scheduler-call comparison."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_irq_context_44900e.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[4]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x44900e-0x438000:0x44903c-0x438000]
assert len(BODY) == 46

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) uint32_t audio_os_scheduler_state_4558a4(void){__asm volatile("bx lr");}\n')
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_irq_context_44900e',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, ipsr, scheduler, primask, basepri):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        for reg, value in ((A.UC_ARM_REG_SP, 0x2000f000),
                           (A.UC_ARM_REG_LR, 0x600001),
                           (A.UC_ARM_REG_IPSR, ipsr),
                           (A.UC_ARM_REG_PRIMASK, primask),
                           (A.UC_ARM_REG_BASEPRI, basepri)):
            cpu.reg_write(reg, value)
        cut = (symbols['audio_os_scheduler_state_4558a4'] & ~1) if compiled else 0x4558a4
        seen = []

        def lower(uc, address, size, _):
            if address != cut: return
            seen.append('scheduler')
            uc.reg_write(A.UC_ARM_REG_R0, scheduler)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_os_irq_context_44900e'] if compiled else 0x44900e
        cpu.emu_start(entry | 1, 0x600000, count=100)
        return seen, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for ipsr in (0, 1, 0x1ff):
        for scheduler in (0, 1, 2):
            for primask in (0, 1):
                for basepri in (0, 0x30):
                    stock = run(False, ipsr, scheduler, primask, basepri)
                    candidate = run(True, ipsr, scheduler, primask, basepri)
                    assert stock == candidate, (ipsr, scheduler, primask, basepri,
                                                stock, candidate)
                    cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-irq-context-44900e'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_IRQ_CONTEXT_44900E', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'lower_boundary': {'audio_os_scheduler_state_4558a4': '0x4558a4'},
           'limits': ['Scheduler state is a controlled lower call.',
                      'Emulated CPU register cases do not establish physical interrupt timing.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
