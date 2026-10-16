#!/usr/bin/env python3
"""Compare stock/C peer ring bit extraction for every packed-status byte."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_peer_ring_status_47d8f0.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ble-peer-ring-status-47d8f0'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'; shim.write_text('#include <stdint.h>\nuint8_t audio_ota_packed_status;\n')
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_peer_ring_status_47d8f0', str(SOURCE),
                        str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, value):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            state = symbols['audio_ota_packed_status'] if compiled else 0x20075043
            uc.mem_write(state, bytes([value]))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = symbols['audio_ble_peer_ring_status_47d8f0'] if compiled else 0x47d8f0
            uc.emu_start(start | 1, 0x600000, count=100)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError('no return')
            return uc.reg_read(A.UC_ARM_REG_R0)
        for value in range(256):
            native, candidate = run(False, value), run(True, value)
            if native != candidate:
                raise AssertionError((value, native, candidate))
        receipt = {'status': 'PASS_NATIVE_MAIN_BLE_PEER_RING_STATUS_47D8F0',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x47d8f0-BASE:0x47d8fc-BASE]).hexdigest(),
                   'cases': 256,
                   'limits': ['All 256 packed-status values compared; final RAM placement and peer synchronization behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], 256, sha(path))

if __name__ == '__main__': main()
