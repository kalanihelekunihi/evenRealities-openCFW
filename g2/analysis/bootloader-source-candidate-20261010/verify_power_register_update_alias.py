#!/usr/bin/env python3
"""Compare startup's power-update alias against locked stock 0x41d92c."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ALIAS = ROOT / 'g2/components/bootloader/source_candidate_20261010/power_register_update_alias.c'
SOURCE = ROOT / 'g2/components/bootloader/clock_manager/clock_class_providers.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, register_id, value, primask):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x10000, 0x10000), (0x20000000, 0x40000),
                         (0x40010000, 0x1000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    u.mem_write(0x40010000, bytes(0x1000))
    u.reg_write(a.UC_ARM_REG_R0, register_id)
    u.reg_write(a.UC_ARM_REG_R1, value)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    pc = (symbols['opencfw_boot_power_register_update'] & ~1) if source else 0x41d92c
    visited, writes, done = set(), [], False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
        elif not source and 0x41d92c <= address < 0x41d9aa:
            visited.update(range(address, address + size))

    def mem_write(cpu, access, address, size, written, _):
        if 0x40010000 <= address < 0x40011000:
            writes.append([address, size, written & ((1 << (8 * size)) - 1)])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(pc | 1, 0, count=1000)
    assert done
    return {'status': u.reg_read(a.UC_ARM_REG_R0),
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK),
            'power_area_sha256': hashlib.sha256(u.mem_read(0x40010000, 0x404)).hexdigest(),
            'writes': writes}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    body = image[0x41d92c - 0x410000:0x41d9aa - 0x410000]
    assert hashlib.sha256(body).hexdigest() == '69608d49656b5685af08e567db6cb31852e5ee8d50767fc393d8bf31c6f2c114'
    with tempfile.TemporaryDirectory(prefix='bootloader-power-update-alias-') as temp:
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
                        str(HERE / 'power-register-update-alias-module.ld'),
                        *(str(x) for x in objects), '-o', str(elf)], check=True,
                       capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        fixtures = [(15, 3), (15, 10), (0, 0), (0, 0x800),
                    (5, 0x2000), (5, 0x4000), (223, 0), (224, 0),
                    (0x1c, 0), (0x1c, 0x13), (0x1c, 0x2000),
                    (0xffffffff, 0xffffffff)]
        compared, visited = [], set()
        for rid, value in fixtures:
            for primask in (0, 1):
                stock, stock_trace = run(False, image, segments, symbols, rid, value, primask)
                candidate, _ = run(True, image, segments, symbols, rid, value, primask)
                assert stock == candidate, (rid, value, primask, stock, candidate)
                visited |= stock_trace
                compared.append({'register_id': rid, 'value': value,
                                 'primask_in': primask, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'original_body_sha256': hashlib.sha256(body).hexdigest(),
                  'stock_entry': '0x41d92d', 'distinct_original_trace_bytes': len(visited),
                  'original_body_bytes': len(body),
                  'alias_sha256': hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected startup_alternatives passes ID 0x1c and a RAM-loaded value in R0/R1.',
                             'MMIO is synthetic RAM; actual register effects are not established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'power-register-update-alias-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
