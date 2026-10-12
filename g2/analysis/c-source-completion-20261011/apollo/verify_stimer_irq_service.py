#!/usr/bin/env python3
"""Bounded Boot tickless IRQ service 0x41b670 child-cut comparison."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
source = ROOT / 'g2/components/bootloader/initializer_callbacks/stimer_irq.c'
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, stubobj, elfpath = directory / 'timer.o', directory / 'stub.o', directory / 'timer.elf'
    cc = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m33', '-mthumb']
    subprocess.run(cc + ['-O2', '-ffreestanding', '-fno-builtin', '-c',
                         str(source), '-o', str(obj)], check=True)
    names = [line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()]
    stub = directory / 'stub.S'
    stub.write_text('.syntax unified\n.thumb\n.text\n' + ''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in names))
    subprocess.run(cc + ['-c', str(stub), '-o', str(stubobj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x500000', '-o', str(elfpath),
                    str(obj), str(stubobj)], check=True, stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
    native_cuts = {0x41f424: 'counter', 0x41f440: 'compare',
                   0x41b2f8: 'mask', 0x418408: 'tick'}
    source_cuts = {symbols[name] & ~1: kind for name, kind in (
        ('opencfw_bl_port_timer_read_counter', 'counter'),
        ('opencfw_bl_port_timer_compare_set', 'compare'),
        ('opencfw_bl_mask_interrupts', 'mask'),
        ('opencfw_bl_tick_increment', 'tick'))}
    cases = 0
    observations = []
    visited = set()
    for last, current, interval, wake in ((100,105,10,0),(100,120,10,0),
                                          (100,120,10,1),(0xfffffff0,5,10,0),
                                          (0xfffffff0,5,10,1),(100,120,0,0),
                                          (100,120,7,1)):
        pair = []
        for native in (True, False):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            cpu.mem_map(0x410000, 0x40000)
            cpu.mem_write(0x410000, stock)
            cpu.mem_map(0x500000, 0x10000)
            if not native:
                for address, payload in segments:
                    cpu.mem_write(address, payload)
            cpu.mem_map(0x20000000, 0x30000)
            cpu.mem_map(0xe000e000, 0x1000)
            cpu.mem_write(0x20027120, struct.pack('<II', last, interval))
            calls = []
            interval_reads = []
            def memory_read(emu, access, address, size, value, _):
                if address == 0x20027124:
                    interval_reads.append(struct.unpack('<I', emu.mem_read(address, 4))[0])
            cpu.hook_add(UC_HOOK_MEM_READ, memory_read)
            cuts = native_cuts if native else source_cuts
            def cut(emu, address, size, _):
                if native and 0x41b670 <= address < 0x41b6e2:
                    visited.update(range(address, address + size))
                if address not in cuts:
                    return
                kind = cuts[address]
                calls.append((kind, emu.reg_read(UC_ARM_REG_R0) if kind == 'compare' else None,
                              emu.reg_read(UC_ARM_REG_R1) if kind == 'compare' else None))
                emu.reg_write(UC_ARM_REG_R0, current if kind == 'counter' else
                              wake if kind == 'tick' else 0)
                emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, cut)
            cpu.reg_write(UC_ARM_REG_SP, 0x2002f000)
            cpu.reg_write(UC_ARM_REG_LR, 0x50f001)
            entry = 0x41b670 if native else symbols['opencfw_boot_stimer_tickless_service'] & ~1
            try:
                cpu.emu_start(entry | 1, 0x50f000, count=2000)
            except Exception as exc:
                raise AssertionError((last,current,interval,wake,native,
                                      hex(cpu.reg_read(UC_ARM_REG_PC)),calls)) from exc
            pair.append((calls, interval_reads, bytes(cpu.mem_read(0x20027120, 8)),
                         bytes(cpu.mem_read(0xe000ed04, 4)),
                         cpu.reg_read(UC_ARM_REG_SP), cpu.reg_read(UC_ARM_REG_PC)))
        assert pair[0] == pair[1], (last,current,interval,wake,pair)
        observations.append({'last': last, 'current': current, 'interval': interval,
                             'wake': wake, 'interval_reads': len(pair[0][1]),
                             'ordered_calls': pair[0][0]})
        cases += 1
    receipt = {'status': 'PASS', 'cases': cases,
               'stock_sha256': hashlib.sha256(stock).hexdigest(),
               'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'isolated_elf_sha256': hashlib.sha256(elfpath.read_bytes()).hexdigest(),
               'body_bytes': 114,
               'visited_body_bytes': len(visited & set(range(0x41b670, 0x41b6e2))),
               'observations': observations,
               'limits': ['Controlled child calls and synthetic tick/SRAM state; no IRQ or physical timer proof.',
                          'Seven interval/wrap/wake cases, including zero divisor; not exhaustive timing histories.']}
    (Path(__file__).with_name('boot-stimer-current-oracle.json')).write_text(
        json.dumps(receipt, indent=2) + '\n')
    print('PASS_BOOT_STIMER_TICKLESS', cases)
