#!/usr/bin/env python3
"""Check known source root producers against co-placement section collection."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUILD = HERE / 'boot-coplacement-gpio-mode-data-round'
ELF = BUILD / 'boot.elf'
INVENTORY = BUILD / 'objects/inventory.json'
VECTORS = ROOT / 'g2/components/bootloader/startup/vectors.S'
RUNTIME = ROOT / 'g2/components/bootloader/initializer_callbacks/startup_runtime.c'
SCATTER = HERE / 'scatter-full-relocations-receipt.json'

inventory = json.loads(INVENTORY.read_text())
providers = set(inventory['global_weak_providers'])
linked = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-a', str(ELF)], text=True).splitlines()
    if len(line.split()) >= 3}
excluded = providers - linked

vector_symbols = [name for name in re.findall(r'^\s*\.word\s+(\S+)',
                                             VECTORS.read_text(), re.M)
                  if not name.startswith('0x') and name != '0']
assert len(re.findall(r'^\s*\.word\s+', VECTORS.read_text(), re.M)) == 256
runtime_symbols = re.findall(
    r'\bslot\(\s*(?:0x[0-9a-fA-F]+|\d+)\s*,\s*'
    r'\(uint32_t\)\(uintptr_t\)&([A-Za-z_][A-Za-z_0-9]*)\s*\)',
    RUNTIME.read_text())
assert len(runtime_symbols) == 31
scatter = json.loads(SCATTER.read_text())
scatter_symbols = [binding['symbol'] for binding in scatter['bindings']]
assert len(scatter_symbols) == 34
root_names = set(vector_symbols + runtime_symbols + scatter_symbols +
                 ['opencfw_boot_manager_task'])
missing = sorted(root_names - linked)
assert not missing, missing
assert not (root_names & excluded)

receipt = {
    'status': 'PASS_KNOWN_SOURCE_ROOTS_SURVIVE_GC',
    'source_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
    'selected_providers': len(providers),
    'linked_provider_names': len(providers & linked),
    'gc_excluded_provider_names': len(excluded),
    'vector_symbol_entries': len(vector_symbols),
    'runtime_slot_assignments': len(runtime_symbols),
    'scatter_callback_bindings': len(scatter_symbols),
    'unique_known_source_roots': len(root_names),
    'known_roots_excluded': missing,
    'limits': [
        'Proves only that the vector, decoded startup callback, selected runtime-slot, and manager-task source symbols survive this experimental section collection.',
        'The excluded provider count is not a missing-body count. Other callback tables, computed/registered roots, and final linker placement require independent analysis.',
    ],
}
(HERE / 'boot-gc-known-roots-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in
                  ('status', 'unique_known_source_roots', 'gc_excluded_provider_names')}))
