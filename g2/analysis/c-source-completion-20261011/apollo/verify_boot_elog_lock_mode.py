#!/usr/bin/env python3
"""Bounded original/source logger lock-mode setter with service calls cut."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from unicorn import arm_const as a

root = Path(__file__).resolve().parents[4]
base_path = root / 'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py'
spec = importlib.util.spec_from_file_location('boot_oracle_base', base_path)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class Machine(base.Machine):
    def __init__(self, source, segments, symbols):
        super().__init__(source, segments, symbols)
        self.events = []
        self.service_addresses = ({
            symbols['opencfw_bl_service_wake'] & ~1: 'wake',
            symbols['opencfw_bl_service_sleep'] & ~1: 'sleep',
        } if source else {0x41a69a: 'wake', 0x41a6a2: 'sleep'})

    def code(self, uc, pc, size, user):
        if pc in self.service_addresses:
            self.events.append(self.service_addresses[pc])
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        super().code(uc, pc, size, user)

    def run_case(self, mode, active, pending):
        self.cpu.mem_write(0x20026700, bytes(256))
        self.cpu.mem_write(0x200267f3, bytes((pending, active)))
        self.cpu.reg_write(a.UC_ARM_REG_SP, base.SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, base.STOP | 1)
        self.cpu.reg_write(a.UC_ARM_REG_R0, mode)
        entry = (self.symbols['opencfw_boot_elog_set_lock_mode'] & ~1
                 if self.source else 0x417b7c)
        self.cpu.emu_start(entry | 1, base.STOP + 2, count=200)
        assert self.done, (self.source, mode, active, pending)
        return (bytes(self.cpu.mem_read(0x200267f2, 3)), tuple(self.events))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory)
        selected = root / 'g2/components/bootloader/initializer_callbacks/elog_output.c'
        fixture = out / 'service_cuts.c'
        fixture.write_text('void opencfw_bl_service_wake(void) {}\n'
                           'void opencfw_bl_service_sleep(void) {}\n')
        for name, source in [('body', selected), ('cuts', fixture)]:
            subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55',
                            '-mthumb', '-mfpu=fpv5-sp-d16', '-mfloat-abi=softfp',
                            '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                            '-ffunction-sections', '-fdata-sections', '-c', str(source),
                            '-o', str(out/(name+'.o'))], check=True)
        subprocess.run(['arm-none-eabi-ld', '--gc-sections', '-Ttext=0x10000',
                        '-e', 'opencfw_boot_elog_set_lock_mode', str(out/'body.o'),
                        str(out/'cuts.o'), '-o', str(out/'source.elf')], check=True)
        _, segments, symbols = base.elf.elf_info(out/'source.elf')
        result = execute_cases(segments, symbols, out/'source.elf')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': result['cases']}))

def execute_cases(segments, symbols, elf_path):
    assert hashlib.sha256(base.BLOB.read_bytes()).hexdigest() == base.LOCKED_SHA
    cases = []
    for mode in (0, 1, 2, 255, 256):
        for active in (0, 1, 2):
            for pending in (0, 1, 2):
                original = Machine(False, segments, symbols).run_case(mode, active, pending)
                selected = Machine(True, segments, symbols).run_case(mode, active, pending)
                assert original == selected, (mode, active, pending, original, selected)
                cases.append((mode, active, pending))
    result = {'status': 'PASS', 'cases': len(cases),
              'stock_sha256': base.LOCKED_SHA,
              'selected_elf_sha256': hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              'cuts': ['service wake/sleep calls return without executing mutex internals'],
              'limits': ['Logger lock-mode register and service-call choice only; no scheduler or physical mutex proof.']}
    return result

if __name__ == '__main__':
    main()
