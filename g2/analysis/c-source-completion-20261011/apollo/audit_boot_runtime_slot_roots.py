#!/usr/bin/env python3
"""Bound selected startup hook producer and its linked function roots."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parents[4]
source = root / 'g2/components/bootloader/initializer_callbacks/startup_runtime.c'
elf = Path(__file__).with_name('boot-coplacement-native-empty-round') / 'boot.elf'
text = source.read_text()
assignments = re.findall(
    r'\bslot\(\s*(0x[0-9a-fA-F]+|\d+)\s*,\s*'
    r'\(uint32_t\)\(uintptr_t\)&([A-Za-z_][A-Za-z_0-9]*)\s*\)', text)
assert len(assignments) == 31
assert len(re.findall(r'\bslot\(', text)) == len(assignments) + 1
assert all(0 <= int(offset, 0) <= 0x38 and int(offset, 0) % 4 == 0
           for offset, _ in assignments)
assert 'for(uint32_t i=0;i<60;i++)B(0x20026e38u+i)=0' in text
defined = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-a', str(elf)], text=True).splitlines()
    if len(line.split()) >= 3}
names = {name for _, name in assignments}
assert names <= defined, sorted(names - defined)
receipt = {
    'status': 'PASS_SOURCE_RUNTIME_SLOT_ROOTS',
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    'slot_assignments': len(assignments),
    'unique_source_function_targets': len(names),
    'slot_offsets': [hex(value) for value in sorted({int(offset, 0)
                                                  for offset, _ in assignments})],
    'target_symbols': sorted(names),
    'unlinked_targets': [],
    'opaque_executable_literal_assignments': 0,
    'limits': [
        'Checks the selected startup_spot_dispatch producer source and linked symbols only.',
        'Firmware revisions and product mode choose branches at runtime; this does not validate all branch effects, other runtime-written tables, or physical hooks.',
    ],
}
out = Path(__file__).with_name('boot-runtime-slot-roots.json')
out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ('status', 'slot_assignments',
                                        'unique_source_function_targets',
                                        'unlinked_targets')}))
