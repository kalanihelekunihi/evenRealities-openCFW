#!/usr/bin/env python3
"""Compare Apollo S200 draw-layer 0x53f400 with its C wrapper."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

root = Path(__file__).resolve().parents[3]
source = root / 'components/main/ambiq_buffer_handlers_candidate_20261014/layer.c'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower = [('audio_uart_checksum_copy', 0x439c04),
         ('audio_uart_ambiq_draw_image_53f42a', 0x53f42a)]

with tempfile.TemporaryDirectory() as directory:
    stub = Path(directory) / 'lower.c'
    stub.write_text('typedef unsigned u32;\n' + '\n'.join(
        f'void {name}(u32 a,u32 b,u32 c){{}}' for name, _ in lower))
    image = Path(directory) / 'layer.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    str(source), str(stub), '-o', str(image)],
                   check=True, capture_output=True)
    with image.open('rb') as file:
        elf = ELFFile(file)
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
        symbols = {sym.name: sym['st_value']
                   for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, layer_value):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, blob)
        uc.mem_map(0x100000, 0x200000)
        uc.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        unit, descriptor, area, layer = (0x20005000, 0x20006000,
                                         0x20007000, 0x20008000)
        original = bytearray((i * 37 + 11) & 255 for i in range(108))
        original[28:32] = layer.to_bytes(4, 'little')
        uc.mem_write(descriptor, bytes(original))
        uc.mem_write(layer, layer_value.to_bytes(4, 'little'))
        calls = []

        def hook(emu, address, size, user):
            name = next(name for name, native in lower
                        if (symbols[name] & ~1 if compiled else native) == address)
            r0, r1, r2 = (emu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            if name == 'audio_uart_checksum_copy':
                calls.append(('copy', r1 == descriptor, r2))
                emu.mem_write(r0, bytes(emu.mem_read(r1, r2)))
            else:
                payload = bytes(emu.mem_read(r1, 108))
                calls.append(('image', r0 == unit, r2 == area, payload))
            emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

        for name, native in lower:
            target = symbols[name] & ~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE, hook, begin=target, end=target)
        uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(UC_ARM_REG_LR, 0x600001)
        for reg, value in ((UC_ARM_REG_R0, unit), (UC_ARM_REG_R1, descriptor),
                           (UC_ARM_REG_R2, area)):
            uc.reg_write(reg, value)
        entry = symbols['audio_uart_ambiq_draw_layer_53f400'] if compiled else 0x53f400
        uc.emu_start(entry | 1, 0x600000, count=200)
        return calls

    for value in (0, 1, 0x2000a000, 0xffffffff):
        native = run(False, value)
        candidate = run(True, value)
        assert native == candidate, (value, native, candidate)
    print('PASS_AMBIQ_DRAW_LAYER_NATIVE', 4)
