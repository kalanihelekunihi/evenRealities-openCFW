#!/usr/bin/env python3
"""Compare source-owned PCM2.2 I-cache disable with locked stock 0x41e22e."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/pcm22_icache_disable.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, guard, cache_control, primask, r0):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for base, length in [(0x08000000, 0x1000), (0x410000, 0x25000),
                         (0x20000000, 0x40000), (0xe0000000, 0x200000)]:
        u.mem_map(base, length)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    for address, value in [(0xe001e300, guard), (0xe000ed14, cache_control),
                           (0xe000ef50, 0xa5a5a5a5)]:
        u.mem_write(address, struct.pack('<I', value))
    u.reg_write(a.UC_ARM_REG_R0, r0)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['opencfw_pcm22_icache_disable'] & ~1) if source else 0x41e22e
    writes, visited, done = [], set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and 0x41e22e <= address < 0x41e266:
            visited.update(range(address, address + size))
        if source:
            assert 0x430000 <= address < 0x431000

    def mem_write(cpu, access, address, size, value, _):
        if 0xe0000000 <= address < 0xe0200000:
            writes.append([address, size, value & ((1 << (size * 8)) - 1)])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(entry | 1, 0, count=300)
    assert done
    return {'return': u.reg_read(a.UC_ARM_REG_R0),
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK),
            'cache_control': struct.unpack('<I', u.mem_read(0xe000ed14, 4))[0],
            'invalidate': struct.unpack('<I', u.mem_read(0xe000ef50, 4))[0],
            'writes': writes}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    body = image[0x41e22e - 0x410000:0x41e266 - 0x410000]
    with tempfile.TemporaryDirectory(prefix='bootloader-pcm22-icache-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'pcm22-icache-disable-module.ld'),
                        str(obj), '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for guard in (0, 0x100, 0x200, 0x300, 0xffffffff):
            for cache_control in (0, 0x20000, 0xa5a5a5a5):
                for primask in (0, 1):
                    stock, trace = run(False, image, segments, symbols,
                                       guard, cache_control, primask, 0x12345678)
                    candidate, _ = run(True, image, segments, symbols,
                                       guard, cache_control, primask, 0x12345678)
                    assert stock == candidate, (guard, cache_control, primask, stock, candidate)
                    visited |= trace
                    compared.append({'guard': guard, 'cache_control': cache_control,
                                     'primask_in': primask, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'original_body_sha256': hashlib.sha256(body).hexdigest(),
                  'stock_entry': '0x41e22f', 'original_body_bytes': len(body),
                  'distinct_original_trace_bytes': len(visited),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['PCM2.2 callers invoke this with no arguments and consume or ignore R0 status.',
                             'SCB/cache MMIO is synthetic RAM; cache invalidation and barrier effects on hardware are not established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'pcm22-icache-disable-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('status', 'cases', 'distinct_original_trace_bytes')}))


if __name__ == '__main__':
    main()
