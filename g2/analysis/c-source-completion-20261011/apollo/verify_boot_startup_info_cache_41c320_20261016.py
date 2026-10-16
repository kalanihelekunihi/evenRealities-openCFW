#!/usr/bin/env python3
"""Compare stock/C boot startup information-cache read chain."""
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
SOURCE = G2 / 'components/bootloader/initializer_callbacks/startup_runtime.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
IMAGE_SHA = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
START, END = 0x41c320, 0x41c480
BODY_SHA = '491e0a58d7c2d1c1adbc0a0f41c0bfaed43225d56db4b10d76962fc41861601c'
OUT = G2 / 'build/c-firmware/20261016/boot-startup-info-cache-41c320'
READS = ((5, 0x480, 2), (1, 0x204, 1), (1, 0x206, 1), (3, 0x208, 8),
         (1, 0x210, 1), (1, 0x240, 3), (1, 0x24a, 2), (1, 0x250, 12),
         (1, 0x245, 1))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA or hashlib.sha256(
            IMAGE[START - 0x410000:END - 0x410000]).hexdigest() != BODY_SHA:
        raise RuntimeError('official bootloader or information-cache body changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n__attribute__((naked)) '
                        'uint32_t opencfw_boot_device_mode_wait(void)'
                        '{__asm volatile("bx lr");}\n')
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-ffunction-sections',
                        '-fdata-sections', '-O2', '-Wall', '-Wextra', '-Werror', '-nostdlib',
                        '-Wl,--gc-sections', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,opencfw_boot_startup_info_cache',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       parsed.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, gate, status_flag, fail_index, seed):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M33)
            uc.mem_map(0x410000, 0x30000); uc.mem_write(0x410000, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments: uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x40000)
            uc.mem_map(0x40000000, 0x30000)
            uc.mem_map(0x08000000, 0x1000)
            uc.mem_write(0x400201bc, u32(gate))
            uc.mem_write(0x40021008, u32(status_flag))
            record = 0x200267f8
            for offset in range(0, 128, 4): uc.mem_write(record + offset, u32(seed))
            uc.reg_write(A.UC_ARM_REG_SP, 0x2003f000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x08000001)
            target = ((symbols['opencfw_boot_device_mode_wait'] & ~1) if compiled
                      else 0x421548)
            calls = []
            def observe(cpu, address, size, _):
                if address == 0x08000000:
                    cpu.emu_stop(); return
                if address != target: return
                regs = tuple(cpu.reg_read(x) for x in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                index = len(calls)
                calls.append(regs[:3])
                if index >= len(READS) or regs[:3] != READS[index]:
                    raise AssertionError(('read sequence changed', index, regs[:3]))
                if index == fail_index:
                    result = 6
                else:
                    for word in range(regs[2]):
                        cpu.mem_write(regs[3] + word * 4,
                                      u32(0x10000000 + index * 0x100 + word))
                    result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['opencfw_boot_startup_info_cache'] if compiled else START
            uc.emu_start(start | 1, 0, count=5000)
            if uc.reg_read(A.UC_ARM_REG_PC) != 0x08000000:
                raise RuntimeError('information-cache body did not return')
            return {'status': uc.reg_read(A.UC_ARM_REG_R0), 'calls': calls,
                    'record': bytes(uc.mem_read(record, 128)).hex()}

        cases = 0
        for gate in (0, 8, 0xffffffff):
            for status_flag in (0, 0x08000000, 0xffffffff):
                for fail_index in range(-1, len(READS)):
                    for seed in (0, 0xa5a5a5a5):
                        native = run(False, gate, status_flag, fail_index, seed)
                        candidate = run(True, gate, status_flag, fail_index, seed)
                        if native != candidate:
                            raise AssertionError((gate, status_flag, fail_index, seed,
                                                  native, candidate))
                        cases += 1
    receipt = {'status': 'PASS_NATIVE_BOOT_STARTUP_INFO_CACHE_41C320',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_bootloader_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
               'cases': cases,
               'limits': ['Device-mode read provider is controlled; guard, nine read calls, failures and 128-byte record are compared. Root composition, live device responses and hardware remain open.']}
    path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))
if __name__ == '__main__': main()
