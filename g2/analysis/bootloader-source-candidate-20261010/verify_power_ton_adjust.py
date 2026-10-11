#!/usr/bin/env python3
"""Compare source-owned event-A TON leaf with locked stock 0x42a1bc."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/power_ton_adjust.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BODY_SHA = '8964efd235151acf974a0248acac460c57de14ed8effbb879293a54d97f6dfd0'
LO, HI = 0x42a1bc, 0x42a2a4
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, minor, major, seed, primask):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x20000000, 0x40000), (0x40000000, 0x300000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    fields = (0x20026bf4, 0x20026bf8, 0x20026bfc, 0x20026c00,
              0x40020344, 0x40020354, 0x40020358)
    for i, address in enumerate(fields):
        u.mem_write(address, struct.pack('<I', (seed ^ (i * 0x9e3779b9)) & 0xffffffff))
    u.reg_write(a.UC_ARM_REG_R0, minor)
    u.reg_write(a.UC_ARM_REG_R1, major)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['event_a_power_ton_adjust'] & ~1) if source else LO
    writes, visited, done = [], set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and LO <= address < HI:
            visited.update(range(address, address + size))
        if source:
            assert 0x430000 <= address < 0x431000

    def mem_write(cpu, access, address, size, value, _):
        if 0x40000000 <= address < 0x40300000:
            writes.append([address, size, value & ((1 << (8 * size)) - 1)])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(entry | 1, 0, count=1000)
    assert done
    return {'writes': writes,
            'registers': {hex(address): struct.unpack('<I', u.mem_read(address, 4))[0]
                          for address in fields},
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK)}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    assert hashlib.sha256(image[LO-0x410000:HI-0x410000]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix='bootloader-ton-adjust-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'power-ton-adjust-module.ld'), str(obj),
                        '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for minor in (*range(10), 0xffffffff):
            for major in (0, 1, 8, 9):
                for seed in (0, 0xa5a5a5a5):
                    for primask in (0, 1):
                        stock, trace = run(False, image, segments, symbols,
                                           minor, major, seed, primask)
                        candidate, _ = run(True, image, segments, symbols,
                                           minor, major, seed, primask)
                        assert stock == candidate, (minor, major, seed,
                                                    primask, stock, candidate)
                        visited |= trace
                        compared.append({'minor': minor, 'major': major,
                                         'seed': seed, 'primask_in': primask,
                                         'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'original_body_sha256': BODY_SHA,
                  'stock_entry': hex(LO | 1), 'original_body_bytes': HI - LO,
                  'distinct_original_trace_bytes': len(visited),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected PCM2.2 callers pass minor and major as full R0/R1 words and ignore return.',
                             'MMIO is synthetic RAM; actual TON/trim/power effects are not established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'power-ton-adjust-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'distinct_original_trace_bytes': len(visited)}))


if __name__ == '__main__':
    main()
