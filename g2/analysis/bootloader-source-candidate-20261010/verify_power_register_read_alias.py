#!/usr/bin/env python3
"""Compare the clockmux read alias with the locked stock register getter."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ALIAS = ROOT / 'g2/components/bootloader/source_candidate_20261010/power_register_read_alias.c'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/startup_power_register_read.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, register_id, output_nonnull, primask, seed):
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
    values = [(seed ^ (i * 0x9e3779b9)) & 0xffffffff for i in range(0xe0)]
    u.mem_write(0x40010000, b''.join(struct.pack('<I', x) for x in values))
    output = 0x20001000
    u.mem_write(output, struct.pack('<I', 0xa5a5a5a5))
    u.reg_write(a.UC_ARM_REG_R0, register_id)
    u.reg_write(a.UC_ARM_REG_R1, output if output_nonnull else 0)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    pc = (symbols['opencfw_power_register_read'] & ~1) if source else 0x41d90e
    visited, done = set(), False

    def hook(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
        elif not source and 0x41d90e <= address < 0x41d92c:
            visited.update(range(address, address + size))

    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start(pc | 1, 0, count=300)
    assert done
    return {'status': u.reg_read(a.UC_ARM_REG_R0),
            'output': struct.unpack('<I', u.mem_read(output, 4))[0],
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK)}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-power-read-alias-') as temp:
        p = Path(temp)
        objects = []
        for source in (ALIAS, SOURCE):
            obj = p / (source.stem + '.o')
            subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55',
                            '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                            '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                            '-c', str(source), '-o', str(obj)], check=True)
            objects.append(obj)
        elf = p / 'source.elf'
        subprocess.run(['arm-none-eabi-ld', '-T', str(HERE / 'power-register-read-alias-module.ld'),
                        *(str(x) for x in objects), '-o', str(elf)], check=True,
                       capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        fixtures = [(0, 1, 0, 0), (15, 1, 1, 0x12345678),
                    (223, 1, 1, 0xffffffff), (0, 0, 0, 0),
                    (15, 0, 1, 0xabcdef01), (223, 0, 0, 0x76543210),
                    (224, 1, 0, 0x12345678), (255, 1, 1, 0xffffffff),
                    (224, 0, 1, 0), (0xffffffff, 1, 0, 0x5a5a5a5a)]
        compared, visited = [], set()
        for rid, valid, irq, seed in fixtures:
            stock, stock_trace = run(False, image, segments, symbols, rid, valid, irq, seed)
            candidate, _ = run(True, image, segments, symbols, rid, valid, irq, seed)
            assert stock == candidate, (rid, valid, irq, seed, stock, candidate)
            visited |= stock_trace
            compared.append({'register_id': rid, 'output_nonnull': bool(valid),
                             'primask': irq, 'seed': seed, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'stock_entry': '0x41d90f',
                  'distinct_original_trace_bytes': len(visited),
                  'original_body_bytes': 0x41d92c - 0x41d90e,
                  'alias_sha256': hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected startup_clockmux calls ID 15 with a valid output pointer.',
                             'MMIO is synthetic RAM; no physical power register behavior is established.',
                             'Compatible M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'power-register-read-alias-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
