#!/usr/bin/env python3
"""Check bounded source-owned Boot product data against the locked image."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, default=HERE / 'boot-coplacement-gpio-mode-data-round/boot.elf')
parser.add_argument('--output', type=Path, default=HERE / 'boot-tail-data-receipt.json')
args = parser.parse_args()
ELF = args.elf.resolve()
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == LOCKED

symbols = {}
for line in subprocess.check_output(['arm-none-eabi-nm', '-S', str(ELF)], text=True).splitlines():
    parts = line.split()
    if len(parts) == 4:
        symbols[parts[3]] = (int(parts[0], 16), int(parts[1], 16))

with ELF.open('rb') as file:
    image = ELFFile(file)
    segments = [(segment['p_vaddr'], segment.data()) for segment in image.iter_segments()
                if segment['p_type'] == 'PT_LOAD']

def source_bytes(name, size):
    address, bound = symbols[name]
    assert bound >= size, (name, bound, size)
    for start, data in segments:
        if start <= address and address + size <= start + len(data):
            return data[address-start:address-start+size]
    raise AssertionError((name, hex(address), size))

checks = [
    (0x43412c, 'opencfw_boot_idle_name', 5),
    (0x43413c, 'opencfw_boot_timer_name', 8),
    (0x434178, 'opencfw_boot_elog_level_suffixes', 24),
    (0x434190, 'opencfw_boot_gpio_mode_bases', 12),
    (0x4341a4, 'opencfw_boot_dfu_thread_name', 4),
    (0x434024, 'opencfw_boot_shared_memory_profile', 5),
    (0x434154, 'opencfw_boot_conditional_power_value', 4),
    (0x434160, 'opencfw_boot_sleep_fields_initial', 4),
    (0x434170, 'opencfw_boot_adc_power_initial', 4),
    (0x434174, 'opencfw_boot_adc_power_final', 4),
    (0x43419c, 'opencfw_boot_post_special_register_value', 4),
]
rows = []
for address, name, size in checks:
    expected = blob[address-0x410000:address-0x410000+size]
    actual = source_bytes(name, size)
    assert actual == expected, (name, hex(address), actual.hex(), expected.hex())
    rows.append({'stock_address': hex(address), 'size': size,
                 'source_symbol': name, 'sha256': hashlib.sha256(actual).hexdigest()})

receipt = {
    'status': 'PASS_BOUNDED_SOURCE_DATA_BYTES',
    'locked_image_sha256': LOCKED,
    'source_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
    'checked_bytes': sum(row['size'] for row in rows),
    'rows': rows,
    'limits': [
        'Checks named semantic data in the current co-placed source ELF, not the entire original tail or final image placement.',
        'Several remaining tail words are compiler literal-pool operands or unqualified product values and are not admitted by this check.',
    ],
}
args.output.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'rows': len(rows),
                  'checked_bytes': receipt['checked_bytes']}))
