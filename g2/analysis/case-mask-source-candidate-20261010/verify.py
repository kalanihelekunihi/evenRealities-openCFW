#!/usr/bin/env python3
"""Rebuild CASE mask helpers and compare exact function-section bytes."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/mask_providers.c'
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
OBJECT = HERE / 'mask_providers.o'
COMPILER = Path('/usr/bin/clang')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert digest(FIRMWARE) == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
    command = [str(COMPILER), '--target=arm-none-eabi', '-mcpu=cortex-m0plus',
               '-mthumb', '-mfloat-abi=soft', '-Os', '-ffreestanding',
               '-fno-builtin', '-ffunction-sections', '-c', str(SOURCE), '-o', str(OBJECT)]
    subprocess.run(command, cwd=ROOT, check=True)
    with OBJECT.open('rb') as stream:
        elf = ELFFile(stream)
        sections = {section.name: section.data() for section in elf.iter_sections()}
    raw = FIRMWARE.read_bytes()[32:]
    extents = {'case_mask_save': (0xf4, 0xfc), 'case_mask_restore': (0xfc, 0x102)}
    bodies = {}
    for name, (start, end) in extents.items():
        actual = sections['.text.' + name]
        assert actual == raw[start:end], (name, actual.hex(), raw[start:end].hex())
        bodies[name] = {'original_address': hex(0x08000000 + start),
                        'length': end - start, 'bytes_hex': actual.hex()}
    result = {'status': 'PASS', 'exact_functions': 2, 'original_bytes': 14,
              'functions': bodies, 'source_sha256': digest(SOURCE),
              'compiler_sha256': digest(COMPILER), 'object_sha256': digest(OBJECT),
              'firmware_sha256': digest(FIRMWARE), 'command': command,
              'scope': 'Exact code-section bytes for two PRIMASK helpers; no whole-image link.'}
    (HERE / 'byte-proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'functions': 2, 'bytes': 14}))


if __name__ == '__main__':
    main()
