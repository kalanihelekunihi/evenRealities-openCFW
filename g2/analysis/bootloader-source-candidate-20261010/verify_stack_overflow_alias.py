#!/usr/bin/env python3
"""Bounded stock/source comparison of the original stack-overflow hook."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ALIAS = ROOT / 'g2/components/bootloader/source_candidate_20261010/stack_overflow_alias.c'
SOURCE = ROOT / 'g2/components/bootloader/thread_creation/terminal_paths_native/terminal_paths.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, tcb, name):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x20000000, 0x40000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    u.mem_write(name, b'worker-test\0')
    u.reg_write(a.UC_ARM_REG_R0, tcb)
    u.reg_write(a.UC_ARM_REG_R1, name)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['opencfw_bl_stack_overflow'] & ~1) if source else 0x41b600
    calls, visited, done = [], set(), False

    def string(address):
        data = bytearray()
        for _ in range(128):
            byte = u.mem_read(address, 1)[0]
            if not byte:
                return bytes(data).hex()
            data.append(byte)
            address += 1
        raise AssertionError('unterminated diagnostic')

    def code(cpu, address, size, _):
        nonlocal done
        if not source and 0x41b600 <= address < 0x41b60c:
            visited.update(range(address, address + size))
        if address == (0x08000100 if source else 0x415fae):
            calls.append(['print', string(cpu.reg_read(a.UC_ARM_REG_R0)),
                          string(cpu.reg_read(a.UC_ARM_REG_R1))])
            cpu.reg_write(a.UC_ARM_REG_R0, 0x1234)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if calls and u.mem_read(address, 2) == b'\x00\xbe':
            done = True
            cpu.emu_stop()
            return
        if source:
            assert 0x430000 <= address < 0x431000 or address == 0x08000100

    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=300)
    assert done and len(calls) == 1
    return {'calls': calls, 'terminal': 'bkpt-zero'}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-stack-overflow-alias-') as temp:
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
                        str(HERE / 'stack-overflow-alias-module.ld'),
                        *(str(x) for x in objects), '-o', str(elf)], check=True,
                       capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for tcb in (0, 0x20001000, 0xdeadbeef):
            for name in (0x20001034, 0x20002000):
                stock, trace = run(False, image, segments, symbols, tcb, name)
                candidate, _ = run(True, image, segments, symbols, tcb, name)
                assert stock == candidate, (tcb, name, stock, candidate)
                visited |= trace
                compared.append({'tcb': tcb, 'name': name, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'stock_entry': '0x41b601',
                  'original_body_bytes': 12, 'distinct_original_trace_bytes': len(visited),
                  'alias_sha256': hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected thread_select passes TCB in R0 and its name pointer at TCB+0x34 in R1.',
                             'Formatter is a controlled cut; BKPT0 is observed but not executed.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'stack-overflow-alias-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
