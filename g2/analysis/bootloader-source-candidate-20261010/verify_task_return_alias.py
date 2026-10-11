#!/usr/bin/env python3
"""Bounded stock/source comparison of RTOS task-return fatal/debug paths."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_READ, UC_MEM_WRITE, UC_MEM_READ
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ALIAS = ROOT / 'g2/components/bootloader/source_candidate_20261010/task_return_alias.c'
SOURCE = ROOT / 'g2/components/bootloader/thread_creation/terminal_paths_native/terminal_paths.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
SP = 0x2003f000
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, critical, release, incoming):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x20000000, 0x40000), (0xfffff000, 0x1000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    u.mem_write(0x200004c4, struct.pack('<I', critical))
    u.reg_write(a.UC_ARM_REG_R0, incoming)
    u.reg_write(a.UC_ARM_REG_SP, SP)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    for i in range(4, 12):
        u.reg_write(getattr(a, f'UC_ARM_REG_R{i}'), 0xaac000 + i)
    entry = (symbols['opencfw_bl_task_return'] & ~1) if source else 0x41b390
    events, visited, done, loads = [], set(), False, 0

    def code(cpu, address, size, _):
        nonlocal done
        if not source and 0x41b390 <= address < 0x41b3ba:
            visited.update(range(address, address + size))
        if address == (0x08000100 if source else 0x41b2f8):
            events.append(['mask'])
            cpu.reg_write(a.UC_ARM_REG_BASEPRI, 48)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if address == 0x08000000:
            events.append(['debug-return', cpu.reg_read(a.UC_ARM_REG_R0),
                           cpu.reg_read(a.UC_ARM_REG_SP),
                           *[cpu.reg_read(getattr(a, f'UC_ARM_REG_R{i}')) for i in range(4, 12)]])
            done = True
            cpu.emu_stop()
            return
        if source:
            assert 0x430000 <= address < 0x431000

    def mem(cpu, access, address, size, value, _):
        nonlocal done, loads
        if access == UC_MEM_WRITE and address == 0xffffffff:
            events.append(['invalid-store', address, size, value,
                           cpu.reg_read(a.UC_ARM_REG_BASEPRI)])
            done = True
            cpu.emu_stop()
        if access == UC_MEM_READ and address == SP - 8 and critical == 0xffffffff:
            loads += 1
            if loads == 3:
                u.mem_write(address, struct.pack('<I', release))

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem)
    u.hook_add(UC_HOOK_MEM_READ, mem)
    try:
        u.emu_start(entry | 1, 0, count=5000)
    except UcError:
        if not done:
            raise
    assert done
    return {'events': events, 'basepri': u.reg_read(a.UC_ARM_REG_BASEPRI)}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-task-return-alias-') as temp:
        p = Path(temp)
        objects = []
        for source in (ALIAS, SOURCE):
            obj = p / (source.stem + '.o')
            subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                            '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                            '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                            '-ffunction-sections', '-fdata-sections',
                            '-c', str(source), '-o', str(obj)], check=True)
            objects.append(obj)
        elf = p / 'source.elf'
        subprocess.run(['arm-none-eabi-ld', '--gc-sections', '-T',
                        str(HERE / 'task-return-alias-module.ld'),
                        *(str(x) for x in objects), '-o', str(elf)], check=True,
                       capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for critical in (0, 0xffffffff):
            for release in (1, 123, 0xffffffff):
                for incoming in (0, 0xdeadbeef):
                    stock, trace = run(False, image, segments, symbols,
                                       critical, release, incoming)
                    candidate, _ = run(True, image, segments, symbols,
                                       critical, release, incoming)
                    assert stock == candidate, (critical, release, incoming, stock, candidate)
                    visited |= trace
                    compared.append({'critical': critical, 'release': release,
                                     'incoming': incoming, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'stock_entry': '0x41b391',
                  'original_body_bytes': 42, 'distinct_original_trace_bytes': len(visited),
                  'alias_sha256': hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected port_start calls without arguments; incoming R0 is unspecified.',
                             'Interrupt mask is a controlled child; invalid store is observed then stopped.',
                             'Debugger release is synthesized at exact SP-8 slot after three polls.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'task-return-alias-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
