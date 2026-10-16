#!/usr/bin/env python3
"""Compare bootloader startup debug-release child with locked stock bytes."""
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
SOURCE = G2 / 'components/bootloader/initializer_callbacks/startup_shutdown.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
IMAGE_SHA = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
START, END = 0x42252e, 0x422574
OUT = G2 / 'build/c-firmware/20261016/boot-shutdown-debug-release-42252e'
STUBS = ('opencfw_bl_mspi_mode_enter', 'opencfw_bl_mspi_mode_leave',
         'opencfw_boot_control_critical_save', 'opencfw_boot_control_delay_status_change',
         'opencfw_boot_control_query', 'opencfw_hal_delay_us')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('official bootloader changed')
    body_sha = hashlib.sha256(IMAGE[START - 0x410000:END - 0x410000]).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n' + '\n'.join(
            f'__attribute__((naked)) uint32_t {name}(void)'
            '{__asm volatile("bx lr");}' for name in STUBS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,opencfw_boot_shutdown_debug_release',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       parsed.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, counter, irq, debug_word, delay_status):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M33)
            uc.mem_map(0x410000, 0x30000); uc.mem_write(0x410000, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments: uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x40000)
            uc.mem_map(0xe000e000, 0x2000)
            uc.mem_map(0x08000000, 0x1000)
            uc.mem_write(0x200271a3, bytes([counter]))
            uc.mem_write(0xe000edfc, u32(debug_word))
            uc.reg_write(A.UC_ARM_REG_PRIMASK, irq)
            uc.reg_write(A.UC_ARM_REG_SP, 0x2003f000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x08000001)
            native = {0x41b8ec: 'critical', 0x41d21c: 'delay'}
            candidate = {symbols['opencfw_boot_control_critical_save'] & ~1: 'critical',
                         symbols['opencfw_boot_control_delay_status_change'] & ~1: 'delay'}
            hooks = candidate if compiled else native
            events = []
            def observe(cpu, address, size, _):
                if address == 0x08000000:
                    cpu.emu_stop(); return
                kind = hooks.get(address)
                if kind is None: return
                regs = [cpu.reg_read(x) for x in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
                if kind == 'critical':
                    events.append(('critical', regs[0], cpu.reg_read(A.UC_ARM_REG_PRIMASK)))
                    cpu.reg_write(A.UC_ARM_REG_R0, irq)
                    cpu.reg_write(A.UC_ARM_REG_PRIMASK, 1)
                else:
                    events.append(('delay', regs[0], regs[1], regs[2], regs[3]))
                    cpu.reg_write(A.UC_ARM_REG_R0, delay_status)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['opencfw_boot_shutdown_debug_release'] if compiled else START
            uc.emu_start(start | 1, 0, count=1000)
            if uc.reg_read(A.UC_ARM_REG_PC) != 0x08000000:
                raise RuntimeError('debug-release did not return')
            return {'events': events, 'status': uc.reg_read(A.UC_ARM_REG_R0),
                    'counter': uc.mem_read(0x200271a3, 1)[0],
                    'debug_word': int.from_bytes(uc.mem_read(0xe000edfc, 4), 'little'),
                    'primask': uc.reg_read(A.UC_ARM_REG_PRIMASK)}

        cases = 0
        for counter in (0, 1, 2, 0x7f, 0xff):
            for irq in (0, 1):
                for debug_word in (0, 0x1000000, 0xffffffff):
                    for delay_status in (0, 3, 6):
                        native, candidate = (run(False, counter, irq, debug_word, delay_status),
                                             run(True, counter, irq, debug_word, delay_status))
                        if native != candidate:
                            raise AssertionError((counter, irq, debug_word, delay_status,
                                                  native, candidate))
                        cases += 1
    receipt = {'status': 'PASS_NATIVE_BOOT_SHUTDOWN_DEBUG_RELEASE_42252E',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_bootloader_sha256': IMAGE_SHA, 'native_body_sha256': body_sha,
               'cases': cases,
               'limits': ['Critical-save and delay-status child calls were controlled; return low word, counter, MMIO and PRIMASK were compared. Startup composition, timing and hardware remain open.']}
    path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))
if __name__ == '__main__': main()
