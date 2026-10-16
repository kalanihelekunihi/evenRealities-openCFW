#!/usr/bin/env python3
"""Compare C and stock six-byte ring-address sentinel checks."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ring_address_is_unset_4a26e8.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ring-address-is-unset-4a26e8'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ring_address_is_unset_4a26e8', str(SOURCE),
                        '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbol = next(s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()
                          if s.name == 'audio_ring_address_is_unset_4a26e8')
        cases = [None, b'\xff' * 6, b'\x00' * 6]
        for position in range(6):
            for value in (0, 1, 0x7f, 0xfe):
                data = bytearray(b'\xff' * 6); data[position] = value
                cases.append(bytes(data))
        for seed in range(64):
            cases.append(bytes(((seed * 37 + j * 53) & 255) for j in range(6)))
        def run(compiled, data):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for addr, body in segments: uc.mem_write(addr, body)
            uc.mem_map(0x20000000, 0x100000)
            if data is not None: uc.mem_write(0x20021000, data)
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, 0 if data is None else 0x20021000)
            uc.emu_start((symbol if compiled else 0x4a26e8) | 1, 0x600000, count=200)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError('function did not return')
            return uc.reg_read(A.UC_ARM_REG_R0)
        for data in cases:
            native, candidate = run(False, data), run(True, data)
            if native != candidate:
                raise AssertionError((data, native, candidate))
        receipt = {'status': 'PASS_NATIVE_MAIN_RING_ADDRESS_IS_UNSET_4A26E8',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x4a26e8-BASE:0x4a271e-BASE]).hexdigest(),
                   'cases': len(cases),
                   'limits': ['Null, all-FF, single-byte mutation and deterministic six-byte inputs only; call-site composition remains separately gated.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], len(cases), sha(path))

if __name__ == '__main__': main()
