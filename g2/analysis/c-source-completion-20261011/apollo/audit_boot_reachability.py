#!/usr/bin/env python3
"""Compare linked Boot source providers with selected archive and a no-GC fit.

This deliberately does not infer that every selected provider is required.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
build = HERE / 'boot-coplacement-locale'
receipt = json.loads((build / 'receipt.json').read_text())
inventory = json.loads((build / 'objects/inventory.json').read_text())
providers = set(inventory['global_weak_providers'])
provider_meta = inventory['global_weak_providers']
symbols = subprocess.check_output(['arm-none-eabi-nm', '--defined-only',
    str(build / 'boot.elf')], text=True)
linked = {line.split()[-1] for line in symbols.splitlines() if len(line.split()) >= 3}
absent = providers - linked
absent_rows = [{'symbol': name,
                'kind': provider_meta[name]['kind'],
                'source': provider_meta[name]['source']}
               for name in sorted(absent)]
by_kind = {kind: sum(row['kind'] == kind for row in absent_rows)
           for kind in sorted({row['kind'] for row in absent_rows})}
by_component = {}
for row in absent_rows:
    component = Path(row['source']).parts[3]
    by_component[component] = by_component.get(component, 0) + 1
command = [arg for arg in receipt['link_command'] if arg != '--gc-sections']
command[command.index('-o') + 1] = str(build / 'boot-no-gc.elf')
command[command.index('-Map') + 1] = str(build / 'boot-no-gc.map')
result = subprocess.run(command, capture_output=True, text=True)
diagnostic = result.stdout + result.stderr
match = re.search(r"region `FLASH' overflowed by (\d+) bytes", diagnostic)
assert result.returncode and match, diagnostic
out = {
    'status': 'PASS_BOUNDED_REACHABILITY_AUDIT',
    'linked_elf_sha256': hashlib.sha256((build / 'boot.elf').read_bytes()).hexdigest(),
    'selected_provider_names': len(providers),
    'linked_selected_provider_names': len(providers & linked),
    'garbage_collected_selected_provider_names': len(absent),
    'garbage_collected_examples': sorted(absent)[:30],
    'garbage_collected_by_kind': by_kind,
    'garbage_collected_by_component': dict(sorted(by_component.items())),
    'garbage_collected_provider_rows': absent_rows,
    'no_gc_overflow_bytes_before_main_preamble': int(match.group(1)),
    'partition_upper_bound': '0x437fe0',
    'main_execution_base': '0x438000',
    'source_elf_file_bytes': receipt['image_file_bytes'],
    'source_elf_partition_headroom_bytes': 0x437fe0 - 0x410000 - receipt['image_file_bytes'],
    'no_gc_link_command': command,
    'limits': [
        'Garbage-collected selected providers include optional library APIs and possibly unmodeled asynchronous routes; these counts are not functional coverage.',
        'The conservative flash end reserves the 32-byte main OTA preamble. The package validator itself checks overlap against 0x438000.',
        'A no-GC overflow is a size observation for this compiler and source set, not proof a complete required image cannot fit after reachability and size work.'
    ]
}
path = HERE / 'boot-reachability-audit.json'
path.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({key: out[key] for key in ('status', 'selected_provider_names',
    'linked_selected_provider_names', 'garbage_collected_selected_provider_names',
    'no_gc_overflow_bytes_before_main_preamble', 'source_elf_partition_headroom_bytes')}))
