#!/usr/bin/env python3
"""Compare stock/C scheduler-state reads across the two native RAM cells."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_scheduler_state_4558a4.c'
UPSTREAM = ROOT / 'third-party/upstream/cmsis-freertos/Source/tasks.c'
UPSTREAM_COMMIT = 'd213f261b5be6bb29a7cce8b84071706b72f4d53'
assert subprocess.check_output(['git', '-C', str(UPSTREAM.parents[1]), 'rev-parse', 'HEAD'],
                               text=True).strip() == UPSTREAM_COMMIT
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x4558a4-0x438000:0x4558c4-0x438000]
assert len(BODY) == 32
RUNNING, SUSPENDED = 0x20074a3c, 0x20074a58

with tempfile.TemporaryDirectory() as temp:
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_scheduler_state_4558a4',
                    '-Wl,--defsym=audio_os_scheduler_running_20074a3c=0x20074a3c',
                    '-Wl,--defsym=audio_os_scheduler_suspended_20074a58=0x20074a58',
                    str(SOURCE), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, running, suspended):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x80000)
        cpu.mem_write(RUNNING, running.to_bytes(4, 'little'))
        cpu.mem_write(SUSPENDED, suspended.to_bytes(4, 'little'))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols['audio_os_scheduler_state_4558a4'] if compiled else 0x4558a4
        cpu.emu_start(entry | 1, 0x600000, count=80)
        return cpu.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for running in (0, 1, 0xffffffff):
        for suspended in (0, 1, 0xffffffff):
            stock = run(False, running, suspended)
            candidate = run(True, running, suspended)
            assert stock == candidate, (running, suspended, stock, candidate)
            cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-scheduler-state-4558a4'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_SCHEDULER_STATE_4558A4', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'attributed_upstream': str(UPSTREAM.relative_to(ROOT)),
           'attributed_upstream_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
           'attributed_upstream_commit': UPSTREAM_COMMIT,
           'ram_cells': [hex(RUNNING), hex(SUSPENDED)],
           'limits': ['Two native scheduler RAM cells remain external.',
                      'This oracle does not verify their initializer ownership or RTOS scheduling.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
