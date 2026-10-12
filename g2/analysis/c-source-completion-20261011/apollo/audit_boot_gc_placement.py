#!/usr/bin/env python3
"""Account for selected Boot sections discarded by the bounded source link.

This is a placement/root audit, not a claim that every discarded section is
stock-reachable. The map is produced by build_boot_coplacement.py.
"""
import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reachability', type=Path)
    args = parser.parse_args()
    build = args.build.resolve()
    lines = (build / 'boot.map').read_text().splitlines()
    first = lines.index('Discarded input sections') + 1
    last = lines.index('Memory Configuration')
    inventory = json.loads((build / 'objects/inventory.json').read_text())
    sources = {int(unit['object'][5:8]): unit['source'] for unit in inventory['units']
               if unit['status'] == 'selected'}
    entries = []
    for i in range(first, last):
        line = lines[i]
        match = re.match(r'\s+(\.[\w.$-]+)\s+0x[0-9a-f]+\s+0x([0-9a-f]+)\s+.*\(unit_(\d+)\.o\)', line)
        if match:
            section, size, number = match.group(1), int(match.group(2), 16), int(match.group(3))
        elif re.match(r'\s+\.[\w.$-]+\s*$', line) and i + 1 < last:
            match = re.match(r'\s+0x[0-9a-f]+\s+0x([0-9a-f]+)\s+.*\(unit_(\d+)\.o\)', lines[i + 1])
            if not match:
                continue
            section, size, number = line.strip(), int(match.group(1), 16), int(match.group(2))
        else:
            continue
        if size and section.startswith(('.text.', '.rodata.', '.data.', '.bss.')):
            entries.append({'section': section, 'bytes': size, 'source': sources.get(number),
                            'object': f'unit_{number:03d}.o'})
    totals = {prefix: {'sections': sum(e['section'].startswith(prefix) for e in entries),
                       'bytes': sum(e['bytes'] for e in entries if e['section'].startswith(prefix))}
              for prefix in ('.text.', '.rodata.', '.data.', '.bss.')}
    receipt = json.loads((build / 'receipt.json').read_text())
    bindings = json.loads((build.parent / 'manual_body_bindings.json').read_text())['bindings']
    by_symbol = {}
    for binding in bindings:
        by_symbol.setdefault(binding['symbol'], []).append(binding['entry'])
    for entry in entries:
        if entry['section'].startswith('.text.'):
            entry['stock_body_bindings'] = by_symbol.get(entry['section'][6:], [])
    if args.reachability:
        reachable = set(json.loads(args.reachability.read_text())['reachable_catalogue_addresses'])
        for entry in entries:
            entry['direct_rooted_stock_bodies'] = [address for address in entry.get('stock_body_bindings', [])
                                                   if hex(int(address, 16)) in reachable]
    bound_discarded = [entry for entry in entries if entry.get('stock_body_bindings')]
    rooted_discarded = [entry for entry in entries if entry.get('direct_rooted_stock_bodies')]
    result = {'build': str(build), 'bounded_link_status': receipt['status'],
              'bounded_image_file_bytes': receipt['image_file_bytes'],
              'main_preamble_boundary_bytes': receipt['partition_bytes_before_main_preamble'],
              'discarded': totals,
              'discarded_sections_with_manually_bound_stock_bodies': len(bound_discarded),
              'discarded_manually_bound_stock_body_bytes': sum(entry['bytes'] for entry in bound_discarded),
              'discarded_sections_with_direct_rooted_stock_bodies': len(rooted_discarded),
              'discarded_direct_rooted_stock_body_bytes': sum(entry['bytes'] for entry in rooted_discarded),
              'entries': sorted(entries, key=lambda e: (-e['bytes'], e['section'])),
              'limits': ['--gc-sections removes archive functions without a relocation from selected roots.',
                         'Function-pointer, registration, native absolute-address, and loader roots require independent proof.',
                         'Discarded sections are candidate placement obligations, not automatically required stock bodies.']}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('bounded_link_status', 'bounded_image_file_bytes', 'main_preamble_boundary_bytes', 'discarded')}))


if __name__ == '__main__':
    main()
