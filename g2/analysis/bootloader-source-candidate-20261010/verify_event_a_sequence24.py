#!/usr/bin/env python3
"""Compare selector-24 callback's two stock bytes with source-owned BX LR."""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/event_a_sequence24.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BODY_SHA = 'c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, arguments, primask):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    u.mem_map(0x08000000, 0x1000)
    u.mem_map(0x410000, 0x25000)
    u.mem_map(0x20000000, 0x40000)
    if source:
        for seg in segments:
            u.mem_write(seg['address'], seg['data'])
    else:
        u.mem_write(0x410000, image)
    for i, value in enumerate(arguments):
        u.reg_write(getattr(a, f'UC_ARM_REG_R{i}'), value)
    for i in range(4, 12):
        u.reg_write(getattr(a, f'UC_ARM_REG_R{i}'), 0xa5a50000 + i)
    u.reg_write(a.UC_ARM_REG_PRIMASK, primask)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['event_a_transition_sequence_24'] & ~1) if source else 0x42a030
    visited, done = set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
        elif not source and address == 0x42a030:
            visited.update(range(address, address + size))
        elif source:
            assert 0x430000 <= address < 0x431000

    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=20)
    assert done
    return {'registers': [u.reg_read(getattr(a, f'UC_ARM_REG_R{i}'))
                          for i in range(12)],
            'sp': u.reg_read(a.UC_ARM_REG_SP),
            'primask': u.reg_read(a.UC_ARM_REG_PRIMASK)}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    body = image[0x42a030-0x410000:0x42a032-0x410000]
    assert body == bytes.fromhex('7047') and hashlib.sha256(body).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix='bootloader-event-a-sequence24-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'event-a-sequence24-module.ld'), str(obj),
                        '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        compared, visited = [], set()
        for r0 in (0, 1, 8, 0xffffffff):
            for r1 in (0, 5, 0xffffffff):
                for r2 in (0, 0x12345678):
                    for r3 in (0, 0xdeadbeef):
                        for primask in (0, 1):
                            args = (r0, r1, r2, r3)
                            stock, trace = run(False, image, segments, symbols, args, primask)
                            candidate, _ = run(True, image, segments, symbols, args, primask)
                            assert stock == candidate, (args, primask, stock, candidate)
                            visited |= trace
                            compared.append({'args': args, 'primask_in': primask,
                                             'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'original_body_sha256': BODY_SHA,
                  'stock_entry': '0x42a031', 'original_body_bytes': 2,
                  'distinct_original_trace_bytes': len(visited),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected callback table invokes selector 24 with four ARM32 words; the stock two-byte body is exactly BX LR.',
                             'No enclosing transition or physical power effect is claimed.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'event-a-sequence24-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'distinct_original_trace_bytes': len(visited)}))


if __name__ == '__main__':
    main()
