#!/usr/bin/env python3
"""Compare stock and compiled C threshold cell, trig argument, and result."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/hub_semantic_motion_threshold_4a4e8c.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x4a4e8c-BASE:0x4a4ec0-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-hub-semantic-motion-threshold-4a4e8c'
HELPERS = ('__aeabi_i2d', '__aeabi_dmul', '__aeabi_ddiv', '__aeabi_d2f')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')
def fbits(value): return int.from_bytes(struct.pack('<f', value), 'little')
def dbits(value): return int.from_bytes(struct.pack('<d', value), 'little')
def from_double(bits): return struct.unpack('<d', bits.to_bytes(8, 'little'))[0]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text(''.join(f'__attribute__((naked)) void {name}(void){{__asm volatile("bx lr");}}\n' for name in HELPERS) +
                        '__attribute__((naked,pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float x){__asm volatile("bx lr");}\n')
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_hub_semantic_motion_threshold_4a4e8c',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, threshold, previous, previous_sine):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            uc.mem_map(0xe000e000, 0x1000)
            uc.mem_write(0xe000ed88, u32(0x00f00000))
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            if not compiled:
                for offset in (0x4a4e98, 0x4a4e9c, 0x4a4ea0,
                               0x4a4ea4, 0x4a4ea8, 0x4a4eac):
                    uc.mem_write(offset, b'\xaf\xf3\x00\x80')  # nop.w; arithmetic hook below
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            cells = ((symbols['audio_hub_motion_threshold_cell'], symbols['audio_hub_motion_threshold_sine_cell'])
                     if compiled else (0x20000e64, 0x200731a8))
            uc.mem_write(cells[0], u32(previous)); uc.mem_write(cells[1], u32(previous_sine))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000); uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, threshold)
            hooks = {symbols[name] & ~1: name for name in HELPERS} if compiled else {}
            hooks[(symbols['audio_uart_float_trig_mode1_50968c'] & ~1) if compiled else 0x50968c] = 'trig'
            trace = []
            radians = [0.0]
            def observe(cpu, address, size, _):
                if not compiled and address in (0x4a4e98, 0x4a4e9c, 0x4a4ea0,
                                                0x4a4ea4, 0x4a4ea8, 0x4a4eac):
                    if address == 0x4a4e98:
                        raw = cpu.reg_read(A.UC_ARM_REG_S0)
                        radians[0] = float(raw if raw < 0x80000000 else raw - 0x100000000)
                    elif address == 0x4a4ea0:
                        radians[0] *= from_double(0x400921fb54442eea)
                    elif address == 0x4a4ea8:
                        radians[0] /= 180.0
                    elif address == 0x4a4eac:
                        cpu.reg_write(A.UC_ARM_REG_S0, fbits(radians[0]))
                    return
                name = hooks.get(address)
                if name is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0); r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                if name == 'trig':
                    arg = cpu.reg_read(A.UC_ARM_REG_S0)
                    trace.append(arg)
                    cpu.reg_write(A.UC_ARM_REG_S0, arg ^ 0x80000000)
                elif name == '__aeabi_i2d':
                    signed = r0 if r0 < 0x80000000 else r0 - 0x100000000
                    bits = dbits(float(signed))
                    cpu.reg_write(A.UC_ARM_REG_R0, bits & 0xffffffff)
                    cpu.reg_write(A.UC_ARM_REG_R1, bits >> 32)
                elif name in ('__aeabi_dmul', '__aeabi_ddiv'):
                    left = from_double(r0 | (r1 << 32))
                    right = from_double(cpu.reg_read(A.UC_ARM_REG_R2) | (cpu.reg_read(A.UC_ARM_REG_R3) << 32))
                    bits = dbits(left * right if name == '__aeabi_dmul' else left / right)
                    cpu.reg_write(A.UC_ARM_REG_R0, bits & 0xffffffff)
                    cpu.reg_write(A.UC_ARM_REG_R1, bits >> 32)
                else:
                    cpu.reg_write(A.UC_ARM_REG_R0, fbits(from_double(r0 | (r1 << 32))))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_hub_semantic_motion_threshold_4a4e8c'] if compiled else 0x4a4e8c
            try:
                uc.emu_start(start | 1, 0x600000, count=200)
            except Exception as exc:
                raise RuntimeError(('emulation failed', compiled, hex(uc.reg_read(A.UC_ARM_REG_PC)))) from exc
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000: raise RuntimeError(('no return', compiled))
            return (uc.reg_read(A.UC_ARM_REG_R0),
                    tuple(int.from_bytes(uc.mem_read(cell, 4), 'little') for cell in cells), trace)
        cases = 0
        for threshold in (0, 1, 2, 45, 90, 180, 360, 0xffffffff, 0xffffffda,
                          0x80000000, 0x7fffffff):
            for previous, previous_sine in ((0, 0), (0xa5a5a5a5, 0x5a5a5a5a)):
                args = (threshold, previous, previous_sine)
                native = run(False, *args); candidate = run(True, *args)
                if native != candidate: raise AssertionError((args, native, candidate))
                cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_HUB_SEMANTIC_MOTION_THRESHOLD_4A4E8C',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Native double VFP instructions, trig callee and C soft-float helpers are controlled arithmetic hooks because Unicorn M-class rejects double VFP; final RAM placement and hardware behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
