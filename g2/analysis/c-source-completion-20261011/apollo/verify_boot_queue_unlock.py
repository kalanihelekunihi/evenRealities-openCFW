#!/usr/bin/env python3
"""Bounded stock/current selected-C queue unlock call and state oracle."""
import hashlib
import json
import pathlib
import struct
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/thread_creation/timer_wait.c'
OUT = HERE / 'boot-queue-unlock-current-oracle.json'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'

with tempfile.TemporaryDirectory() as scratch:
    scratch = pathlib.Path(scratch)
    obj, stub_obj, elf_path = scratch / 'source.o', scratch / 'cuts.o', scratch / 'source.elf'
    cc = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin', '-c',
                         str(SOURCE), '-o', str(obj)], check=True)
    unresolved = [line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()]
    stub = scratch / 'cuts.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in unresolved))
    subprocess.run(cc + ['-c', str(stub), '-o', str(stub_obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x500000', '-o', str(elf_path),
                    str(obj), str(stub_obj)], check=True, stderr=subprocess.DEVNULL)
    with elf_path.open('rb') as fh:
        elf = ELFFile(fh)
        segments = [(seg['p_vaddr'], seg.data()) for seg in elf.iter_segments()
                    if seg['p_type'] == 'PT_LOAD' and seg.data()]
        names = {sym.name: sym['st_value'] for sec in elf.iter_sections()
                 if sec.header.sh_type == 'SHT_SYMTAB' for sym in sec.iter_symbols()}

    stock_cuts = {0x41b3e4: 'enter', 0x41b3fc: 'exit',
                  0x41872c: 'remove', 0x4189a2: 'yield'}
    source_cuts = {names[name] & ~1: kind for name, kind in (
        ('opencfw_bl_kernel_enter', 'enter'), ('opencfw_bl_kernel_exit', 'exit'),
        ('opencfw_bl_remove_event_waiter', 'remove'),
        ('opencfw_bl_missed_yield', 'yield'))}

    def put(cpu, addr, value):
        cpu.mem_write(addr, struct.pack('<I', value & 0xffffffff))

    def get(cpu, addr):
        return struct.unpack('<I', cpu.mem_read(addr, 4))[0]

    def run(stock, tx_lock, rx_lock, tx_count, rx_count):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        for base, size in ((0x410000, 0x25000), (0x500000, 0x10000),
                           (0x20000000, 0x30000), (0x600000, 0x1000)):
            cpu.mem_map(base, size)
        if stock:
            cpu.mem_write(0x410000, blob)
        else:
            for base, payload in segments:
                if 0x500000 <= base < 0x510000:
                    cpu.mem_write(base, payload)
        queue = 0x20020000
        put(cpu, queue + 36, tx_count)
        put(cpu, queue + 16, rx_count)
        cpu.mem_write(queue + 68, bytes((rx_lock & 255, tx_lock & 255)))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2002f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
        cpu.reg_write(A.UC_ARM_REG_R0, queue)
        calls, visited, done = [], set(), []
        cuts = stock_cuts if stock else source_cuts

        def hook(c, pc, size, _):
            if pc == 0x600000:
                done.append(True)
                c.emu_stop()
            elif pc in cuts:
                kind = cuts[pc]
                if kind == 'remove':
                    anchor = c.reg_read(A.UC_ARM_REG_R0)
                    old = get(c, anchor)
                    assert old > 0
                    put(c, anchor, old - 1)
                    calls.append((kind, anchor - queue))
                    c.reg_write(A.UC_ARM_REG_R0, 1)
                else:
                    calls.append((kind, None))
                    c.reg_write(A.UC_ARM_REG_R0, 0)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            if stock and 0x41a556 <= pc < 0x41a5c4:
                visited.update(range(pc, pc + size))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x41a556 if stock else names['opencfw_boot_timer_queue_unlock'] & ~1
        cpu.emu_start(entry | 1, 0x600002, count=2000)
        assert done, (stock, tx_lock, rx_lock, tx_count, rx_count)
        return (calls, bytes(cpu.mem_read(queue, 80))), visited

    cases, visited = [], set()
    for tx_lock, rx_lock, tx_count, rx_count in (
        (-1, -1, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0),
        (1, 1, 1, 1), (2, 3, 2, 3), (3, 2, 1, 3),
        (127, 127, 3, 2), (-128, 1, 2, 1)):
        original, hit = run(True, tx_lock, rx_lock, tx_count, rx_count)
        candidate, _ = run(False, tx_lock, rx_lock, tx_count, rx_count)
        assert original == candidate, (tx_lock, rx_lock, tx_count, rx_count,
                                       original, candidate)
        visited |= hit
        cases.append({'tx_lock': tx_lock, 'rx_lock': rx_lock,
                      'tx_count': tx_count, 'rx_count': rx_count,
                      'calls': original[0],
                      'queue_sha256': hashlib.sha256(original[1]).hexdigest()})
    result = {'status': 'PASS', 'stock_sha256': hashlib.sha256(blob).hexdigest(),
              'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'isolated_elf_sha256': hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              'cases': cases, 'body_bytes': 110,
              'visited_body_bytes': len(visited & set(range(0x41a556, 0x41a5c4))),
              'limits': ['Controlled enter/exit, event removal and yield children; synthetic queue/list state.',
                         'No asynchronous wake, scheduler, physical IRQ or full image proof.']}
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], len(cases), result['visited_body_bytes'])
