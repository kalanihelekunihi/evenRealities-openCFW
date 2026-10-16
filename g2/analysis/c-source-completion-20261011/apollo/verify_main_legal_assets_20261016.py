#!/usr/bin/env python3
"""Verify C object bytes and pointer relocations against all 38 stock assets."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_assets.c'
HEADER = G2 / 'components/audio/uart_thread_source_candidate/legal_regulatory_assets.h'
MANIFEST = G2 / 'analysis/c-source-completion-20261011/apollo/legal-regulatory-assets-provenance.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261016/main-legal-assets'
BASE = 0x438000

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    manifest = json.loads(MANIFEST.read_text())
    image = PAYLOAD.read_bytes()[32:]
    if manifest['official_payload_sha256'] != sha(image) or \
            manifest['source_sha256'] != sha(SOURCE.read_bytes()) or \
            manifest['header_sha256'] != sha(HEADER.read_bytes()) or \
            len(manifest['rows']) != 38:
        raise RuntimeError('legal asset provenance changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'legal-regulatory-assets.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    with obj.open('rb') as f:
        elf = ELFFile(f)
        symtab = elf.get_section_by_name('.symtab')
        symbols = {s.name: s for s in symtab.iter_symbols()}
        def data(name):
            sym = symbols[name]
            section = elf.get_section(sym['st_shndx'])
            return section.data()[sym['st_value']:sym['st_value'] + sym['st_size']]
        table = symbols['audio_legal_asset_slots']
        if table['st_size'] != 38 * 4:
            raise RuntimeError('legal asset pointer table size changed')
        relocs = [r for section in elf.iter_sections()
                  if isinstance(section, RelocationSection) and
                     section['sh_info'] == table['st_shndx']
                  for r in section.iter_relocations()]
        offsets = {r['r_offset'] for r in relocs}
        expected_offsets = {table['st_value'] + 4*i for i in range(38)}
        for row in manifest['rows']:
            name = row['symbol']
            stock = int(row['stock_pointer'], 16)
            if row['kind'] == 'text':
                expected = image[stock-BASE:stock-BASE+row['bytes']]
                if data(name) != expected or sha(expected) != row['sha256']:
                    raise RuntimeError(f'legal text bytes changed: {name}')
            else:
                descriptor = image[stock-BASE:stock-BASE+28]
                compiled = data(name)
                pixel_name = 'legal_pixels_' + row['slot'][2:]
                pixels = data(pixel_name)
                pixel_addr = int(row['pixel_stock_pointer'], 16)
                expected_pixels = image[pixel_addr-BASE:pixel_addr-BASE+row['pixel_bytes']]
                if len(compiled) != 28 or compiled[:16] != descriptor[:16] or \
                        compiled[20:] != descriptor[20:] or \
                        sha(descriptor) != row['descriptor_sha256'] or \
                        pixels != expected_pixels or sha(pixels) != row['pixel_sha256'] or \
                        int.from_bytes(compiled[16:20], 'little') != symbols[pixel_name]['st_value']:
                    raise RuntimeError(f'legal image data changed: {name}')
                expected_offsets.add(symbols[name]['st_value'] + 16)
        if offsets != expected_offsets or len(relocs) != 48:
            raise RuntimeError('legal asset pointer relocation graph changed')
    receipt = {'status': 'PASS_SOURCE_OWNED_MAIN_LEGAL_ASSETS',
               'rows': 38, 'images': 10, 'texts': 28,
               'pixel_bytes': sum(r.get('pixel_bytes', 0) for r in manifest['rows']),
               'provenance': str(MANIFEST.relative_to(ROOT)), 'provenance_sha256': sha(MANIFEST.read_bytes()),
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE.read_bytes()),
               'header': str(HEADER.relative_to(ROOT)), 'header_sha256': sha(HEADER.read_bytes()),
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj.read_bytes()),
               'relocations': len(relocs),
               'limits': ['Data bytes and relocatable pointers are source-owned; final stock placement and UI behavior remain unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['rows'], receipt['pixel_bytes'], sha(path.read_bytes()))

if __name__ == '__main__': main()
