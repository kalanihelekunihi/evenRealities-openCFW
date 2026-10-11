#!/usr/bin/env python3
"""Compare source-owned event-A trim dispatcher with stock 0x42a4bc."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/source_candidate_20261010/power_trims_update.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
BODY_SHA = '7bc6936adbff287072bfdcdac3b453214f98f9604c11239abef5a15f63b5e9bb'
LO, HI = 0x42a4bc, 0x42a546
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/bootloader/update_core/elf_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def run(source, image, segments, symbols, args, child_status, selector):
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
    u.mem_write(0x20000158, struct.pack('<I', 0x08000201) * 256)
    for i, value in enumerate(args):
        u.reg_write(getattr(a, f'UC_ARM_REG_R{i}'), value)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    entry = (symbols['event_a_power_trims_update'] & ~1) if source else LO
    events, visited, done = [], set(), False

    def code(cpu, address, size, _):
        nonlocal done
        if address == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and LO <= address < HI:
            visited.update(range(address, address + size))
        children = {
            (0x08000100 if source else 0x42a1bc): 'ton',
            (0x08000110 if source else 0x42a43a): 'temperature',
            (0x08000120 if source else 0x42a2b4): 'sequence',
            0x08000200: 'dispatch',
        }
        if address in children:
            kind = children[address]
            words = [cpu.reg_read(getattr(a, f'UC_ARM_REG_R{i}')) for i in range(4)]
            if kind == 'sequence':
                pointer = words[2]
                before = u.mem_read(pointer, 1)[0]
                events.append([kind, words[:2], before])
                u.mem_write(pointer, bytes([selector]))
                cpu.reg_write(a.UC_ARM_REG_R0, child_status)
            else:
                events.append([kind, words[:2] if kind == 'ton' else words])
                cpu.reg_write(a.UC_ARM_REG_R0, 0x1234)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if source:
            assert 0x430000 <= address < 0x431000

    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start(entry | 1, 0, count=1000)
    assert done
    return {'events': events}, visited


def main():
    image = BLOB.read_bytes()
    assert hashlib.sha256(image).hexdigest() == LOCKED
    assert hashlib.sha256(image[LO-0x410000:HI-0x410000]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix='bootloader-power-trims-update-') as temp:
        p = Path(temp)
        obj, elf = p / 'source.o', p / 'source.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33',
                        '-mthumb', '-mfloat-abi=soft', '-ffreestanding',
                        '-fno-builtin', '-std=c11', '-O2', '-fwrapv',
                        '-c', str(SOURCE), '-o', str(obj)], check=True)
        subprocess.run(['arm-none-eabi-ld', '-T',
                        str(HERE / 'power-trims-update-module.ld'), str(obj),
                        '-o', str(elf)], check=True, capture_output=True)
        _, segments, symbols = reader.elf_info(elf)
        fixtures = [(0, 0, 0, 0), (1, 1, 3, 3), (1, 1, 3, 2),
                    (4, 5, 2, 1), (5, 4, 2, 1), (8, 0, 7, 0),
                    (9, 2, 1, 3), (0, 8, 0, 7),
                    (0xffffffff, 0xfffffffc, 7, 2)]
        compared, visited = [], set()
        for args in fixtures:
            for child_status in (0, 5):
                for selector in (0, 0x1a, 0xff):
                    stock, trace = run(False, image, segments, symbols,
                                       args, child_status, selector)
                    candidate, _ = run(True, image, segments, symbols,
                                       args, child_status, selector)
                    assert stock == candidate, (args, child_status, selector,
                                                stock, candidate)
                    visited |= trace
                    compared.append({'args': args, 'child_status': child_status,
                                     'selector': selector, 'result': stock})
        report = {'status': 'PASS', 'cases': len(compared),
                  'original_sha256': LOCKED, 'original_body_sha256': BODY_SHA,
                  'stock_entry': hex(LO | 1), 'original_body_bytes': HI - LO,
                  'distinct_original_trace_bytes': len(visited),
                  'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                  'comparisons': compared,
                  'limits': ['Selected startup-events callers pass four full ARM32 words R0-R3 and ignore incidental return.',
                             'TON, temperature, sequence and indirect dispatch children are controlled cuts.',
                             'No physical power/thermal effect, scheduler or callback-table provenance is established by this isolated run.',
                             'M33 execution is compared; M55 archive compilation is separate.']}
        (HERE / 'power-trims-update-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'cases': len(compared),
                          'distinct_original_trace_bytes': len(visited)}))


if __name__ == '__main__':
    main()
