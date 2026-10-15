#!/usr/bin/env python3
"""Bind pinned Cordio and exact ROM data into the fresh Apollo source set."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-coherent-dependencies-round1046'
out.mkdir(parents=True, exist_ok=True)
analysis = root / 'analysis/c-source-completion-20261011/peripherals'
base_receipt = json.loads((root / 'build/c-firmware/ble-source-aggregate-round1045/receipt.json').read_text())
base = root / base_receipt['linked_object']
assert hashlib.sha256(base.read_bytes()).hexdigest() == base_receipt['linked_sha256']
steps = [
    ('verify_cordio_calc128_round1010.py', 'cordio-calc128-round1010/calc128.o'),
    ('verify_cordio_bda_round1011.py', 'cordio-bda-round1011/bda.o'),
    ('verify_cordio_wstr_round1012.py', 'cordio-wstr-round1012/wstr.o'),
    ('verify_radio_rom_literals_round1036.py', 'radio-rom-literals-round1036/radio_strings.o'),
    ('verify_hci_rom_tables_round1037.py', 'hci-rom-tables-round1037/event_sizes.o'),
    (None, 'hci-rom-tables-round1037/dm_hci_route_table.o'),
    ('verify_radio_rom_tail_round1038.py', 'radio-rom-tail-round1038/radio_tail.o'),
]
objects = []
for verifier, relative in steps:
    if verifier is not None:
        subprocess.run([sys.executable, str(analysis / verifier)], check=True,
                       stdout=subprocess.DEVNULL)
    obj = root / 'build/c-firmware' / relative
    assert obj.is_file(), obj
    objects.append(obj)
compare_source = root / 'components/audio/file_sync_candidate/byte_compare.c'
subprocess.run([sys.executable, str(analysis / 'verify_byte_compare.py')], check=True,
               stdout=subprocess.DEVNULL)
compare_obj = out / 'byte_compare.o'
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(compare_source), '-o', str(compare_obj)
], check=True)
objects.append(compare_obj)

def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', *flags, str(path)], text=True).splitlines()}

before = names(base, '-u')
base_defined = names(base, '-g', '--defined-only')
provided = set()
for obj in objects:
    defined = names(obj, '-g', '--defined-only')
    assert not (provided & defined), sorted(provided & defined)
    provided |= defined
assert not (provided & base_defined), sorted(provided & base_defined)
linked = out / 'apollo-main-ble-coherent-dependencies.o'
subprocess.run(['arm-none-eabi-ld', '-r', str(base), *map(str, objects), '-o', str(linked)], check=True)
after = names(linked, '-u')
assert before - after == provided & before and not after - before
assert len(before - after) == 40, len(before - after)
receipt = {
    'round': 1046,
    'status': 'PASS_BLE_COHERENT_DEPENDENCIES_BINDING',
    'component': 'Apollo source-coherent pinned Cordio utilities and exact ROM data',
    'base_object': str(base.relative_to(root)),
    'base_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
    'byte_compare_source': str(compare_source.relative_to(root)),
    'byte_compare_source_sha256': hashlib.sha256(compare_source.read_bytes()).hexdigest(),
    'objects': [{'path': str(obj.relative_to(root)), 'sha256': hashlib.sha256(obj.read_bytes()).hexdigest()}
                for obj in objects],
    'providers_bound': len(before - after),
    'additional_source_providers': len(provided - before),
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Pinned upstream and byte-exact data objects do not establish full ROM placement',
              'Full image layout, startup, binary equality and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before - after), len(before), len(after), receipt['linked_sha256'])
