#!/usr/bin/env python3
"""Bounded stock/source output comparison for 0x59188e."""
from pathlib import Path
import hashlib, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import (
    UC_ARM_REG_D0, UC_ARM_REG_D1, UC_ARM_REG_D2, UC_ARM_REG_LR,
    UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_C1_C0_2, UC_ARM_REG_FPEXC,
    UC_ARM_REG_FPSCR,
)
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGE = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
EXPECTED_IMAGE = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == EXPECTED_IMAGE
start, end = 0x59188e, 0x5918b0
stock = blob[start - 0x437fe0:end - 0x437fe0]
assert hashlib.sha256(stock).hexdigest() == 'c5293fd63b23610d5d29beb387445a5bbf93f4f92bd72879ab193a8dd26f2d7c'
compiler = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
obj = Path('/tmp/audio_dsp_clamp.o')
flags = ['-c', '-mcpu=cortex-m55', '-mthumb', '-mfpu=fpv5-d16',
         '-mfloat-abi=hard', '-O0', '-ffreestanding', '-fno-builtin']
subprocess.run([str(compiler), *flags, str(HERE / 'dsp_clamp.c'), '-o', str(obj)], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    source = elf.get_section_by_name('.text').data()
    source_entry = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                        if s.name == 'g2_audio_dsp_clamp')

def bits(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]

def run(code, address, values, entry_offset=0, fpscr=0):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(address & ~0xfff, 0x1000)
    u.mem_write(address, code)
    u.mem_map(0x20000000, 0x1000)
    u.mem_map(0x10000000, 0x1000)
    u.reg_write(UC_ARM_REG_C1_C0_2, 0xf00000)
    u.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
    u.reg_write(UC_ARM_REG_FPSCR, fpscr)
    u.reg_write(UC_ARM_REG_SP, 0x20000ff0)
    u.reg_write(UC_ARM_REG_LR, 0x10000001)
    for reg, value in zip((UC_ARM_REG_D0, UC_ARM_REG_D1, UC_ARM_REG_D2), values):
        u.reg_write(reg, value)
    u.emu_start((address + entry_offset) | 1, 0x10000000, count=100)
    assert u.reg_read(UC_ARM_REG_PC) == 0x10000000
    return u.reg_read(UC_ARM_REG_D0), u.reg_read(UC_ARM_REG_FPSCR)

qnan = 0x7ff8000000000001
snan = 0x7ff0000000000001
cases = [
    ('inside', (bits(0.25), bits(-1), bits(1))),
    ('below', (bits(-2), bits(-1), bits(1))),
    ('above', (bits(2), bits(-1), bits(1))),
    ('lower_equal', (bits(-1), bits(-1), bits(1))),
    ('upper_equal', (bits(1), bits(-1), bits(1))),
    ('negative_zero', (bits(-0.0), bits(0.0), bits(1))),
    ('positive_zero', (bits(0.0), bits(-0.0), bits(1))),
    ('qnan_value', (qnan, bits(-1), bits(1))),
    ('qnan_lower', (bits(0), qnan, bits(1))),
    ('qnan_upper', (bits(0), bits(-1), qnan)),
    ('snan_value', (snan, bits(-1), bits(1))),
    ('snan_lower', (bits(0), snan, bits(1))),
    ('snan_upper', (bits(0), bits(-1), snan)),
    ('negative_qnan_value', (0xfff8000000000001, bits(-1), bits(1))),
    ('subnormal', (1, bits(-1), bits(1))),
    ('positive_inf', (bits(float('inf')), bits(-1), bits(1))),
    ('negative_inf', (bits(-float('inf')), bits(-1), bits(1))),
    ('reversed_bounds', (bits(0), bits(1), bits(-1))),
]
records = []
for preset in (0, 1, 0x00400000, 0x00800000):
  for name, values in cases:
    original = run(stock, start, values, fpscr=preset)
    compiled = run(source, 0x10001000, values, source_entry, preset)
    assert original == compiled, (name, hex(preset), original, compiled)
    records.append(dict(case=name, initial_fpscr=hex(preset), output=hex(original[0]),
                        stock_fpscr=hex(original[1]), compiled_fpscr=hex(compiled[1])))
report = dict(status='PASS', cases=len(records), image_sha256=EXPECTED_IMAGE,
              stock_body_sha256=hashlib.sha256(stock).hexdigest(),
              source_sha256=hashlib.sha256((HERE / 'dsp_clamp.c').read_bytes()).hexdigest(),
              compiler=str(compiler), compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),
              compiler_flags=flags,
              object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(), results=records,
              limits='D0 output bits and FPSCR compared on synthetic values and four initial FPSCR modes. Stack traffic and non-ABI registers may differ. All higher DSP functions remain unproven.')
(HERE / 'clamp-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS', len(records))
