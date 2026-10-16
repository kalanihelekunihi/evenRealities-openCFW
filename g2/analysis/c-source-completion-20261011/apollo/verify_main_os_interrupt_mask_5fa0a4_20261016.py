#!/usr/bin/env python3
"""Compare stock/C BASEPRI mask leaf on Cortex-M emulation."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_interrupt_mask_5fa0a4.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x5fa0a4-0x438000:0x5fa0ba-0x438000]
assert len(BODY) == 22

with tempfile.TemporaryDirectory() as temp:
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_os_interrupt_mask_5fa0a4',
                    str(SOURCE), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, basepri):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(A.UC_ARM_REG_BASEPRI, basepri)
        entry = symbols['audio_os_interrupt_mask_5fa0a4'] if compiled else 0x5fa0a4
        cpu.emu_start(entry | 1, 0x600000, count=100)
        return (cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1),
                cpu.reg_read(A.UC_ARM_REG_BASEPRI))

    cases = 0
    for basepri in (0, 1, 0x20, 0x30, 0x80, 0xff):
        stock = run(False, basepri)
        candidate = run(True, basepri)
        assert stock == candidate, (basepri, stock, candidate)
        cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-os-interrupt-mask-5fa0a4'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_OS_INTERRUPT_MASK_5FA0A4', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'limits': ['Emulated BASEPRI and barrier execution do not establish hardware timing.',
                      'Final code placement remains open.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
