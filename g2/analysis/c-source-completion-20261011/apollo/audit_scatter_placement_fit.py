#!/usr/bin/env python3
"""Check selected callback object sizes against authenticated stock envelopes.

This is a placement constraint, not equivalence testing. Source functions may
be placed elsewhere if the final image owns the corresponding pointer values.
"""
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
build = HERE / 'boot-source-audit-build'
inventory = json.loads((build / 'inventory.json').read_text())
scatter = json.loads((HERE / 'scatter-full-relocations-receipt.json').read_text())
catalogue = {int(row['entry'], 16): row for row in map(json.loads,
    (ROOT / 'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl').open())}
units = {unit['source']: unit for unit in inventory['units'] if unit['status'] == 'selected'}
rows = []
for binding in scatter['bindings']:
    unit = units[binding['provider']]
    output = subprocess.check_output(['arm-none-eabi-nm', '-S', '-g',
                                      str(build / unit['object'])], text=True)
    pattern = r'^([0-9a-fA-F]+) ([0-9a-fA-F]+) [TW] ' + re.escape(binding['symbol']) + r'$'
    match = re.search(pattern, output, re.M)
    assert match, binding
    native_entry = int(binding['stock_pointer'], 16) & ~1
    native = catalogue.get(native_entry)
    source_size = int(match.group(2), 16)
    rows.append({
        'symbol': binding['symbol'],
        'stock_entry': hex(native_entry),
        'stock_envelope_bytes': native['body_bytes'] if native else None,
        'selected_object_bytes': source_size,
        'exceeds_stock_envelope': native is not None and source_size > native['body_bytes'],
        'object': unit['object'],
    })
result = {
    'scope': 'selected 337-unit Boot archive; section size before final relocation and relaxation',
    'callback_pointer_rows': len(rows),
    'stock_catalogue_envelopes': sum(row['stock_envelope_bytes'] is not None for row in rows),
    'selected_functions_exceeding_stock_envelope': sum(row['exceeds_stock_envelope'] for row in rows),
    'limitations': [
        'Oversize forbids same-entry same-envelope placement for this exact selected object; source can move and the table can relocate in a fresh layout.',
        'A non-oversize function is not proved byte equivalent or finally placeable by this size check.',
        'The bounded callback oracle used explicit stock-address symbol definitions and did not link these final functions at those addresses.'
    ],
    'rows': rows,
}
(HERE / 'scatter-placement-fit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('callback_pointer_rows', 'stock_catalogue_envelopes', 'selected_functions_exceeding_stock_envelope')}))
