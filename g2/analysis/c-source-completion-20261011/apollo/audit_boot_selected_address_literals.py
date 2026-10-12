#!/usr/bin/env python3
"""Bound opaque stock-address literals in selected Boot C/assembly inputs."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INVENTORY = HERE / 'boot-coplacement-gpio-mode-data-round/objects/inventory.json'
inventory = json.loads(INVENTORY.read_text())
selected = [unit for unit in inventory['units'] if unit['status'] == 'selected']
assert len(selected) == inventory['counts']['selected'] == 371

found = []
for unit in selected:
    path = ROOT / unit['source']
    raw = path.read_text(errors='replace')
    # Treat documentation and string metadata as data, not C expression uses.
    code = re.sub(r'/\*.*?\*/|//[^\n]*', ' ', raw, flags=re.S)
    code = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '""', code)
    for match in re.finditer(r'(?<![\w])0x[0-9a-fA-F]+\b', code):
        value = int(match.group(), 16)
        if 0x410000 <= value <= 0x434477:
            found.append({'source': unit['source'], 'address': hex(value)})

assert found == [{'source': 'g2/components/bootloader/startup/record_dispatch.c',
                  'address': '0x410000'}], found
receipt = {
    'status': 'PASS_SELECTED_STOCK_ADDRESS_LITERAL_AUDIT',
    'inventory_sha256': hashlib.sha256(INVENTORY.read_bytes()).hexdigest(),
    'selected_source_units': len(selected),
    'stock_range': ['0x410000', '0x434477'],
    'literal_exceptions': found,
    'opaque_nonbase_stock_literals': 0,
    'limits': [
        'Static lexical scan of selected C and assembly source expressions; the sole 0x410000 literal is the authenticated VTOR image base.',
        'Computed addresses, macro expansion from external headers, runtime state, linker expressions, and future selected source changes require separate review.',
    ],
}
(HERE / 'boot-selected-address-literals.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'selected_source_units': len(selected),
                  'opaque_nonbase_stock_literals': 0}))
