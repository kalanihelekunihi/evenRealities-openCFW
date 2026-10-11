#!/usr/bin/env python3
"""Stock S0 to candidate softfp R0 comparison for PCM2.1 classifier."""
from pathlib import Path
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'g2/components/audio/pcm21_classify_source_candidate/classify.c'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, path = directory / 'classify.o', directory / 'classify.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mfpu=fpv4-sp-d16', '-mfloat-abi=softfp', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-o', str(path), str(obj)], check=True)
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(item['p_vaddr'], item.data()) for item in elf.iter_segments() if item['p_type'] == 'PT_LOAD']
        symbols = {item.name: item['st_value'] for item in elf.get_section_by_name('.symtab').iter_symbols()}

    def evaluate(native, word):
        machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        machine.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        machine.mem_map(0x438000, (len(STOCK) + 4095) & ~4095)
        machine.mem_map(0x100000, 0x20000)
        machine.mem_map(0x20000000, 0x1000)
        machine.mem_write(0x438000, STOCK)
        if not native:
            for address, data in segments:
                machine.mem_write(address, data)
        machine.reg_write(A.UC_ARM_REG_S0, word)
        machine.reg_write(A.UC_ARM_REG_R0, word)
        machine.reg_write(A.UC_ARM_REG_SP, 0x20000800)
        machine.reg_write(A.UC_ARM_REG_LR, 0x101181)
        done = [False]
        def hook(unit, pc, _size, _user):
            if pc == 0x101180:
                done[0] = True
                unit.emu_stop()
        machine.hook_add(UC_HOOK_CODE, hook)
        machine.emu_start((0x5a0a70 if native else symbols['pcm21_classify']) | 1, 0, count=200)
        assert done[0], (native, hex(word))
        return machine.reg_read(A.UC_ARM_REG_R0)

    values = [-1000., -274., -273., -272.999, -21., -20., -19.999,
              -1., -0.0, 0., 0.0001, 49.999, 50., 50.001,
              999.999, 1000., 1001., float('inf'), -float('inf')]
    bits = [struct.unpack('<I', struct.pack('<f', value))[0] for value in values]
    bits += [0x7fc00000, 0x7f800001, 0xffc00000, 0x00000001, 0x80000001]
    for word in bits:
        original, candidate = evaluate(True, word), evaluate(False, word)
        assert original == candidate, (hex(word), original, candidate)
    print('PASS_PCM21_CLASSIFY', len(bits))
