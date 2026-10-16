#!/usr/bin/env python3
"""Compare the defined RGB888 bytes of stock/C LV color_make."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_lv_color_make_441068.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY_SHA = 'ff5cb043efe52cc6bcf2739b72d88c08f0e901ea479204396ddbd4065c263944'
OUT = G2 / 'build/c-firmware/20261016/main-lv-color-make-441068'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA or hashlib.sha256(
            IMAGE[0x441068-0x438000:0x44107c-0x438000]).hexdigest() != BODY_SHA:
        raise RuntimeError('stock payload or color_make body changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_page_441068', str(SOURCE), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, rgb):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(0x438000, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments: uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x100000)
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2), rgb):
                uc.reg_write(reg, value)
            start = symbols['audio_uart_page_441068'] if compiled else 0x441068
            uc.emu_start(start | 1, 0x600000, count=100)
            return uc.reg_read(A.UC_ARM_REG_R0) & 0xffffff
        cases = 0
        for red in (0, 1, 0x55, 0xff, 0x100, 0x12345678):
            for green in (0, 2, 0xaa, 0xff, 0x100, 0x87654321):
                for blue in (0, 3, 0xcc, 0xff, 0x100, 0xa5a5a5a5):
                    rgb = (red, green, blue)
                    if run(False, rgb) != run(True, rgb):
                        raise AssertionError((rgb, run(False, rgb), run(True, rgb)))
                    cases += 1
    receipt = {'status': 'PASS_NATIVE_MAIN_LV_COLOR_MAKE_441068',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
               'cases': cases,
               'limits': ['Only defined RGB888 bytes compared; stock high byte is unspecified.']}
    path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))
if __name__ == '__main__': main()
