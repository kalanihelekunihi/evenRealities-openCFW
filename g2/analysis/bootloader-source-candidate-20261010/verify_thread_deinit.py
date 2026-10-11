#!/usr/bin/env python3
"""Compare source-owned DFU/manager thread teardown leaves with stock."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/thread_deinit.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRIES = {'dfu': ('opencfw_boot_dfu_thread_deinit_native', 0x42ddda, 0x42ddf2, 0x200004d4),
           'manager': ('opencfw_boot_manager_thread_deinit', 0x42e3ca, 0x42e3e0, 0x200004fc)}
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, kind, initial, replacement, child_return, incoming):
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
    name, lo, hi, slot = ENTRIES[kind]
    u.mem_write(slot, struct.pack('<I', initial))
    u.reg_write(a.UC_ARM_REG_R0, incoming)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
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
        child = (address == 0x416200 if not source else
                 address == (0x08000100 if kind == 'dfu' else 0x08000110))
        if child:
            events.append(['terminate', cpu.reg_read(a.UC_ARM_REG_R0)])
            if replacement is not None:
                cpu.mem_write(slot, struct.pack('<I', replacement))
            cpu.reg_write(a.UC_ARM_REG_R0, child_return)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if source:
            assert 0x430000 <= address < 0x431000

    def mem_write(cpu, access, address, size, value, _):
        if address == slot:
            writes.append([address, size, value & 0xffffffff])

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_MEM_WRITE, mem_write)
    u.emu_start(entry | 1, 0, count=300)
    assert done
    return {'return': u.reg_read(a.UC_ARM_REG_R0),
            'slot': struct.unpack('<I', u.mem_read(slot, 4))[0],
            'events': events, 'writes': writes}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    with tempfile.TemporaryDirectory(prefix='bootloader-thread-deinit-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'thread-deinit-module.ld'),
                        str(obj), '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], {kind: set() for kind in ENTRIES}
        for kind in ENTRIES:
            for initial in (0, 0x20003000, 0xffffffff):
                for replacement in (None, 0x20004000):
                    for child_return in (0, 7):
                        for incoming in (0, 0xdeadbeef):
                            stock, trace = run(False, image, segments, symbols,
                                               kind, initial, replacement, child_return, incoming)
                            candidate, _ = run(True, image, segments, symbols,
                                               kind, initial, replacement, child_return, incoming)
                            assert stock == candidate, (kind, initial, replacement,
                                                        child_return, incoming, stock, candidate)
                            visited[kind] |= trace
                            compared.append({'kind': kind, 'initial': initial,
                                             'replacement': replacement,
                                             'child_return': child_return,
                                             'incoming': incoming, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED,
                  'original_bodies': {kind: {'entry': hex(lo | 1), 'bytes': hi - lo,
                                             'visited': len(visited[kind]),
                                             'sha256': hashlib.sha256(image[lo-0x410000:hi-0x410000]).hexdigest()}
                                      for kind, (_, lo, hi, _) in ENTRIES.items()},
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Initializer record entries call both functions with no arguments and consume R0 status.',
                             'Thread termination is controlled; scheduling, quiescence and actual task deletion are not established.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'thread-deinit-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'visited': {kind: len(x) for kind, x in visited.items()}}))


if __name__ == '__main__':
    main()
