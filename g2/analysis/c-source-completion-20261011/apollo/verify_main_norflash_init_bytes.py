#!/usr/bin/env python3
"""Verify the source-owned constant FAL init leaf against locked Main."""
import argparse
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
parser = argparse.ArgumentParser()
parser.add_argument('--object', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
image = STOCK.read_bytes()
assert hashlib.sha256(image).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with args.object.open('rb') as stream:
    source = ELFFile(stream).get_section_by_name('.text.g2_norflash_init_540ed0').data()
native = image[0x540ed0-0x437fe0:0x540ed4-0x437fe0]
assert source == native == bytes.fromhex('00207047')
result = {
    'status': 'PASS_MAIN_NORFLASH_INIT_STOCK_BYTES',
    'native_entry': '0x540ed0',
    'bytes': len(native),
    'native_and_source_sha256': hashlib.sha256(native).hexdigest(),
    'source_object_sha256': hashlib.sha256(args.object.read_bytes()).hexdigest(),
    'limits': ['Only the constant-success init leaf is covered. Read, write, erase, hardware, and the complete Main image remain open.']
}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], result['bytes'])
