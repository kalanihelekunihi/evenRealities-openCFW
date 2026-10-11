#!/usr/bin/env python3
"""Bounded stock/source comparison of the original heap-failure hook."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ALIAS = ROOT / 'g2/components/bootloader/source_candidate_20261010/malloc_failed_alias.c'
SOURCE = ROOT / 'g2/components/bootloader/thread_creation/terminal_paths_native/terminal_paths.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, r0, r1):
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
    u.reg_write(a.UC_ARM_REG_R0, r0)
    u.reg_write(a.UC_ARM_REG_R1, r1)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['opencfw_bl_malloc_failed'] & ~1) if source else 0x41b5f6
    calls, visited, repeats, done = [], set(), {}, False

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
        if not source and 0x41b5f6 <= address < 0x41b600:
            visited.update(range(address, address + size))
        if address == (0x08000100 if source else 0x415fae):
            calls.append(['print', string(cpu.reg_read(a.UC_ARM_REG_R0))])
            cpu.reg_write(a.UC_ARM_REG_R0, 0x1234)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if calls:
            repeats[address] = repeats.get(address, 0) + 1
            if repeats[address] == 4:
                done = True
                cpu.emu_stop()
        if source:
            assert 0x430000 <= address < 0x431000 or address == 0x08000100

    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=300)
    assert done and len(calls) == 1
    return {'calls': calls, 'terminal': 'spin-after-print'}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-malloc-failed-alias-') as temp:
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
                        str(HERE / 'malloc-failed-alias-module.ld'),
                        *(str(x) for x in objects), '-o', str(elf)], check=True,
                       capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for r0 in (0, 1, 0xdeadbeef):
            for r1 in (0, 0x20001000):
                stock, trace = run(False, image, segments, symbols, r0, r1)
                candidate, _ = run(True, image, segments, symbols, r0, r1)
                assert stock == candidate, (r0, r1, stock, candidate)
                visited |= trace
                compared.append({'r0': r0, 'r1': r1, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'stock_entry': '0x41b5f7',
                  'original_body_bytes': 10, 'distinct_original_trace_bytes': len(visited),
                  'alias_sha256': hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['The stock and source formatter are controlled cuts; exact diagnostic bytes and spin request agree.',
                             'Neither physical fault handling nor terminal scheduling is exercised.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'malloc-failed-alias-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
