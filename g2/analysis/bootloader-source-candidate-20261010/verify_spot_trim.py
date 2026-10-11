#!/usr/bin/env python3
"""Compare source-owned spot trim leaves with locked stock bodies."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/spot_trim.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRIES = {'profile': ('native_spot_profile_trim_42ae24', 0x42ae24, 0x42ae6c,
                       '73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538'),
           'restore': ('native_spot_trim_restore_42ae6c', 0x42ae6c, 0x42ae9c,
                       'fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8')}
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, kind, argument, seed, guard):
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
    words = (0x40020088, 0x400201b0, 0x40020080, 0x40020044, 0x4002004c,
             0x20026c08, 0x200270a4, 0x200270a8, 0x200270ac)
    for i, address in enumerate(words):
        u.mem_write(address, struct.pack('<I', (seed ^ (i * 0x9e3779b9)) & 0xffffffff))
    u.mem_write(0x200271ae, bytes([guard]))
    u.reg_write(a.UC_ARM_REG_R0, argument)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    name, lo, hi, _ = ENTRIES[kind]
    entry = (symbols[name] & ~1) if source else lo
    writes, visited, done = [], set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and lo <= address < hi:
            visited.update(range(address, address + size))
        if source:
            assert 0x430000 <= address < 0x431000

    def mem_write(cpu, access, address, size, value, _):
        if 0x40000000 <= address < 0x40300000:
            writes.append([address, size, value & ((1 << (8 * size)) - 1)])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(entry | 1, 0, count=500)
    assert done
    return {'writes': writes,
            'registers': {hex(address): struct.unpack('<I', u.mem_read(address, 4))[0]
                          for address in words}}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    for _, lo, hi, digest in ENTRIES.values():
        assert hashlib.sha256(image[lo-0x410000:hi-0x410000]).hexdigest() == digest
    with tempfile.TemporaryDirectory(prefix='bootloader-spot-trim-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'spot-trim-module.ld'), str(obj), '-o', str(elf)],
                       check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], {kind: set() for kind in ENTRIES}
        for kind in ENTRIES:
            for argument in (0, 1, 255, 0x100, 0xffffffff):
                for seed in (0, 0xa5a5a5a5, 0xffffffff):
                    for guard in (0, 1, 255):
                        stock, trace = run(False, image, segments, symbols,
                                           kind, argument, seed, guard)
                        candidate, _ = run(True, image, segments, symbols,
                                           kind, argument, seed, guard)
                        assert stock == candidate, (kind, argument, seed, guard, stock, candidate)
                        visited[kind] |= trace
                        compared.append({'kind': kind, 'argument': argument,
                                         'seed': seed, 'guard': guard, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED,
                  'original_bodies': {kind: {'entry': hex(lo | 1), 'bytes': hi - lo,
                                             'visited': len(visited[kind]), 'sha256': digest}
                                      for kind, (_, lo, hi, digest) in ENTRIES.items()},
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected PCM2.1 callers pass literal 1 in R0 for profile trim and no argument for trim restore; incidental returns are ignored.',
                             'The source profile entry explicitly tests the low R0 byte, matching stock even for raw R0=0x100. Selected caller declarations use uint8_t and pass literal 1; the machine-level call uses the same R0 word.',
                             'MMIO is synthetic RAM; power and analog effects are not established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'spot-trim-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'visited': {kind: len(x) for kind, x in visited.items()}}))


if __name__ == '__main__':
    main()
