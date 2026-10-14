#!/usr/bin/env python3
"""Compare source-owned FAL product rows with the authenticated Main image."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
UPSTREAM = ROOT / 'third-party/reference/rt-thread-fal/inc/fal_def.h'
BASE = 0x437fe0

parser = argparse.ArgumentParser()
parser.add_argument('--object', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
image = STOCK.read_bytes()
assert hashlib.sha256(image).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
header = UPSTREAM.read_text()
assert 'FAL_DEV_NAME_MAX 24' in header
assert 'struct fal_partition' in header
assert 'uint32_t magic_word;' in header
assert 'char flash_name[FAL_DEV_NAME_MAX];' in header
assert 'long offset;' in header
assert 'size_t len;' in header
assert 'uint32_t reserved;' in header
expected_rows = image[0x6d5358-BASE:0x6d5358-BASE+128]
expected_count = image[0x78f0a8-BASE:0x78f0a8-BASE+4]
expected_device = image[0x722b30-BASE:0x722b30-BASE+56]
expected_table = image[0x78f0a4-BASE:0x78f0a4-BASE+4]
assert len(expected_rows) == 128 and expected_count == struct.pack('<I', 1)
assert expected_table == struct.pack('<I', 0x722b30)
callback_offsets = (36, 40, 44, 48)
callback_names = ('g2_norflash_init_540ed0', 'g2_norflash_read_540ed4',
                  'g2_norflash_write_540f2c', 'g2_norflash_erase_540f84')
callback_addresses = (0x540ed1, 0x540ed5, 0x540f2d, 0x540f85)
with args.object.open('rb') as stream:
    elf = ELFFile(stream)
    rows = elf.get_section_by_name('.rodata.g2_fal_partition_rows').data()
    count = elf.get_section_by_name('.rodata.g2_fal_flash_device_count').data()
    device = elf.get_section_by_name('.rodata.g2_fal_norflash').data()
    table = elf.get_section_by_name('.rodata.g2_fal_flash_device_table').data()
    symtab = elf.get_section_by_name('.symtab')
    def relocations(name):
        section = elf.get_section_by_name(name)
        return [(row['r_offset'], row['r_info_type'],
                 symtab.get_symbol(row['r_info_sym']).name)
                for row in section.iter_relocations()]
    device_relocs = relocations('.rel.rodata.g2_fal_norflash')
    table_relocs = relocations('.rel.rodata.g2_fal_flash_device_table')
assert rows == expected_rows and count == expected_count
assert len(device) == 56 and table == b'\0' * 4
assert device_relocs == [(offset, 2, name) for offset, name in
                         zip(callback_offsets, callback_names)]
assert table_relocs == [(0, 2, 'g2_fal_norflash')]
assert [struct.unpack_from('<I', expected_device, offset)[0] for offset in callback_offsets] == list(callback_addresses)
for index, (source, stock) in enumerate(zip(device, expected_device)):
    if not any(offset <= index < offset+4 for offset in callback_offsets):
        assert source == stock, index
result = {
    'status': 'PASS_MAIN_FAL_PRODUCT_CONFIG_RELOCATIONS',
    'stock_sha256': hashlib.sha256(image).hexdigest(),
    'upstream_header_sha256': hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
    'source_object_sha256': hashlib.sha256(args.object.read_bytes()).hexdigest(),
    'partition_native_start': '0x6d5358',
    'partition_rows': 2,
    'partition_bytes': 128,
    'partition_sha256': hashlib.sha256(rows).hexdigest(),
    'flash_device_count': 1,
    'flash_device_native_start': '0x722b30',
    'flash_device_noncallback_bytes_compared': 40,
    'flash_device_callback_relocations': [
        {'offset': offset, 'native_pointer': hex(address), 'source_symbol': name}
        for offset, address, name in zip(callback_offsets, callback_addresses, callback_names)
    ],
    'flash_device_table_relocations': 1,
    'limits': [
        'The flash device record and table are source-owned with five relocations; callback implementation and link resolution require separate verification.',
        'The upstream FAL layout is pinned at v1.0.0; this byte comparison does not prove the original vendor commit.',
        'Main image layout, FAL physical reads/writes and hardware remain unverified.'
    ]
}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], result['partition_bytes'], len(result['flash_device_callback_relocations']))
