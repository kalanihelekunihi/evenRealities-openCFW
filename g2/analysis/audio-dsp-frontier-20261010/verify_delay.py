#!/usr/bin/env python3
"""Compare stock delay-angle wrapper with source, sharing stock asin body."""
from pathlib import Path
import hashlib, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_D0, UC_ARM_REG_D1, UC_ARM_REG_D2,
    UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP, UC_ARM_REG_C1_C0_2,
    UC_ARM_REG_FPEXC, UC_ARM_REG_FPSCR)
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMAGE = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == SHA
stock = blob[0x5918b0-0x437fe0:0x5918cc-0x437fe0]
assert hashlib.sha256(stock).hexdigest() == '3bfc72be8b8bdc7511bdae236d3bfa0a5bfa01c785522731ab2b090729a52549'
compiler = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path = Path('/tmp/audio_dsp_delay.elf')
flags = ['-mcpu=cortex-m55', '-mthumb', '-mfpu=fpv5-d16', '-mfloat-abi=hard',
         '-O0', '-ffreestanding', '-fno-builtin', '-nostdlib',
         '-Wl,-Ttext=0x10001000', '-Wl,-e,g2_audio_dsp_delay_to_angle',
         '-Wl,--defsym=stock_asin=0x43c261']
subprocess.run([str(compiler), *flags, str(HERE/'delay_to_angle.c'), str(HERE/'dsp_clamp.c'),
                '-o', str(elf_path)], check=True)
with elf_path.open('rb') as f:
    elf = ELFFile(f)
    entry = next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
                 if s.name == 'g2_audio_dsp_delay_to_angle')
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']

def bits(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]

def run(address, values, initial_fpscr=0, stop_at_asin=False):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x437000, ((len(blob) + 0xfe0 + 0xfff)//0x1000)*0x1000)
    u.mem_write(0x437fe0, blob)
    u.mem_map(0x10000000, 0x10000)
    for va, data in segments: u.mem_write(va, data)
    u.mem_map(0x20000000, 0x800000)
    u.reg_write(UC_ARM_REG_C1_C0_2, 0xf00000)
    u.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
    u.reg_write(UC_ARM_REG_FPSCR, initial_fpscr)
    u.reg_write(UC_ARM_REG_SP, 0x207ff000)
    u.reg_write(UC_ARM_REG_LR, 0x10000001)
    for reg, value in zip((UC_ARM_REG_D0, UC_ARM_REG_D1, UC_ARM_REG_D2), values):
        u.reg_write(reg, value)
    asin = []
    def hook(emu, pc, size, data):
        if pc == 0x43c260:
            asin.append((emu.reg_read(UC_ARM_REG_D0), emu.reg_read(UC_ARM_REG_FPSCR)))
            if stop_at_asin: emu.emu_stop()
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start(address | 1, 0x10000000, count=100000)
    if stop_at_asin:
        assert len(asin) == 1 and u.reg_read(UC_ARM_REG_PC) == 0x43c260
        return asin[0]
    assert len(asin) == 1 and u.reg_read(UC_ARM_REG_PC) == 0x10000000
    return (u.reg_read(UC_ARM_REG_D0), u.reg_read(UC_ARM_REG_FPSCR))

cases = [
    ('zero', (bits(0), bits(.14), bits(343))),
    ('lag_minus_10', (bits(-10/16000), bits(.14), bits(343))),
    ('lag_minus_3', (bits(-3/16000), bits(.14), bits(343))),
    ('lag_minus_1', (bits(-1/16000), bits(.14), bits(343))),
    ('lag_plus_1', (bits(1/16000), bits(.14), bits(343))),
    ('lag_plus_3', (bits(3/16000), bits(.14), bits(343))),
    ('lag_plus_10', (bits(10/16000), bits(.14), bits(343))),
    ('negative_zero', (bits(-0.0), bits(.14), bits(343))),
    ('positive_inf', (bits(float('inf')), bits(.14), bits(343))),
    ('negative_inf', (bits(-float('inf')), bits(.14), bits(343))),
    ('quiet_nan', (0x7ff8000000000001, bits(.14), bits(343))),
    ('signaling_nan', (0x7ff0000000000001, bits(.14), bits(343))),
    ('zero_spacing', (bits(0), bits(0), bits(343))),
]
rows=[]
for preset in (0, 1):
    for name, values in cases:
        stock_boundary = run(0x5918b0, values, preset, True)
        source_boundary = run(entry, values, preset, True)
        assert stock_boundary == source_boundary, ('asin_entry',name,hex(preset),stock_boundary,source_boundary)
        stock_result = run(0x5918b0, values, preset)
        source_result = run(entry, values, preset)
        assert stock_result == source_result, ('return',name,hex(preset),stock_result,source_result)
        rows.append(dict(case=name, initial_fpscr=hex(preset), asin_d0=hex(stock_boundary[0]),
                         asin_fpscr=hex(stock_boundary[1]), result_d0=hex(stock_result[0]),
                         result_fpscr=hex(stock_result[1])))
receipt=dict(status='PASS', cases=len(rows), stock_body_sha256=hashlib.sha256(stock).hexdigest(),
             image_sha256=SHA, elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),
             compiler=str(compiler), compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),
             flags=flags, rows=rows, limit='Synthetic double inputs, stock asin shared as authenticated external provider; no full asin source, no hardware execution.')
(HERE/'delay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows))
