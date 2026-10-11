#!/usr/bin/env python3
"""Stock/source comparison of PCM2.2 spot-timer start and stop leaves."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/pcm22_spot_timer.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRIES = {'start': ('opencfw_pcm22_spot_timer_start', 0x41cc48, 0x41cc92),
           'stop': ('opencfw_pcm22_spot_timer_stop', 0x41ccd6, 0x41cd1a)}
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, kind, wait, seed, child_status, primask):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x20000000, 0x40000), (0x40000000, 0x300000),
                         (0xe0000000, 0x200000), (0x47ff0000, 0x1000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    addresses = (0x400083e8, 0x40008010, 0x400083e0,
                 0x40008068, 0xe000e108, 0xe000e188, 0xe000e288,
                 0x47ff0000)
    for i, address in enumerate(addresses):
        u.mem_write(address, struct.pack('<I', (seed ^ (i * 0x9e3779b9)) & 0xffffffff))
    u.reg_write(a.UC_ARM_REG_R0, wait)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    name, lo, hi = ENTRIES[kind]
    entry = (symbols[name] & ~1) if source else lo
    events, writes, visited, done = [], [], set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and lo <= address < hi:
            visited.update(range(address, address + size))
        request = (0x08000100 if source else 0x4222f0)
        release = (0x08000110 if source else 0x422364)
        if address in (request, release):
            events.append(['request' if address == request else 'release',
                           cpu.reg_read(a.UC_ARM_REG_R0), cpu.reg_read(a.UC_ARM_REG_R1)])
            cpu.reg_write(a.UC_ARM_REG_R0, child_status)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if source:
            assert 0x430000 <= address < 0x431000

    def mem_write(cpu, access, address, size, value, _):
        if (0x40000000 <= address < 0x40300000 or
                0xe0000000 <= address < 0xe0200000):
            writes.append([address, size, value & ((1 << (8 * size)) - 1)])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(entry | 1, 0, count=1000)
    assert done
    return {'events': events, 'writes': writes,
            'registers': {hex(address): struct.unpack('<I', u.mem_read(address, 4))[0]
                          for address in addresses},
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK)}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-pcm22-spot-timer-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'pcm22-spot-timer-module.ld'),
                        str(obj), '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], {kind: set() for kind in ENTRIES}
        for kind in ENTRIES:
            for wait in (0, 1, 17, 0x12345678, 0xffffffff):
                for seed in (0, 0xa5a5a5a5):
                    for child_status in (0, 7):
                        for primask in (0, 1):
                            stock, trace = run(False, image, segments, symbols,
                                               kind, wait, seed, child_status, primask)
                            candidate, _ = run(True, image, segments, symbols,
                                               kind, wait, seed, child_status, primask)
                            assert stock == candidate, (kind, wait, seed, child_status,
                                                        primask, stock, candidate)
                            visited[kind] |= trace
                            compared.append({'kind': kind, 'wait': wait, 'seed': seed,
                                             'child_status': child_status,
                                             'primask_in': primask, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED,
                  'original_bodies': {kind: {'entry': hex(lo | 1), 'bytes': hi - lo,
                                             'visited': len(visited[kind]),
                                             'sha256': hashlib.sha256(image[lo-0x410000:hi-0x410000]).hexdigest()}
                                      for kind, (_, lo, hi) in ENTRIES.items()},
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected PCM2.2 callers pass wait in R0 for start; stop is no-argument. Both ignore incidental return registers.',
                             'Clock request/release are controlled; MMIO is synthetic RAM. No physical timer/interrupt/timing effect is established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'pcm22-spot-timer-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'visited': {kind: len(x) for kind, x in visited.items()}}))


if __name__ == '__main__':
    main()
