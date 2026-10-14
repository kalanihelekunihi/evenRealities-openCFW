#!/usr/bin/env python3
"""Compare discarded Boot symbols with conservative native direct reachability."""
import hashlib
import json
import argparse
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PLACEMENT = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/root-boot-current-placement-round448/current-placement.json'
INVENTORY = ROOT / 'g2/build/c-firmware/20261013/root-boot-gate-refresh-round447-final/apollo_bootloader/objects/inventory.json'
CROSSWALK = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/boot-body-crosswalk-hf2-store-order-round.json'
REACH = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/boot-root-reachability-hf2-store-order-round.json'
MANUAL = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/manual_body_bindings.json'
REVIEWED = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/boot-gc-reviewed-paths.json'
parser = argparse.ArgumentParser()
parser.add_argument('--placement', type=Path, default=PLACEMENT)
parser.add_argument('--inventory', type=Path, default=INVENTORY)
parser.add_argument('--output', type=Path, default=HERE / 'gc-reachability-audit.json')
args = parser.parse_args()
P = json.loads(args.placement.read_text())
I = json.loads(args.inventory.read_text())
C = json.loads(CROSSWALK.read_text())
R = json.loads(REACH.read_text())
M = json.loads(MANUAL.read_text())
V = json.loads(REVIEWED.read_text())
assert P['selected_relocatable_definitions'] == 1012
assert len(P['unretained_selected_global_symbols']) <= 206
assert C['locked_image_sha256'] == R['original_sha256'] == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
reachable = {int(x, 16) for x in R['reachable_catalogue_addresses']}
functions = [row for row in C['functions'] if int(row['entry'], 16) in reachable]
reviewed = {row['symbol']: row for row in V['reviewed_paths']}
manual = {}
for row in M['bindings']:
    manual.setdefault(row['symbol'], []).append(row)
rows = []
for name in P['unretained_selected_global_symbols']:
    provider = I['global_weak_providers'].get(name)
    source = provider['source'] if provider else None
    exact = [row for row in functions if row['name'] == name]
    same_source = [row for row in functions if source in row.get('selected_source_leads', [])] if source else []
    manual_reachable = [row for row in manual.get(name, []) if int(row['entry'], 16) in reachable]
    category = ('reviewed_selected_call_path' if name in reviewed else
                'reachable_reviewed_manual_binding_needs_path' if manual_reachable else
                'same_native_name_reachable_needs_path' if exact else
                'source_file_has_reachable_native_lead' if same_source else
                'no_direct_reachability_lead_for_source_file' if source else
                'selected_symbol_without_inventory_provider')
    rows.append({'symbol': name, 'source': source, 'category': category,
                 'same_name_native_entries': [row['entry'] for row in exact],
                 'manual_reachable_native_entries': [row['entry'] for row in manual_reachable],
                 'reviewed_retained_caller': reviewed[name]['retained_caller'] if name in reviewed else None,
                 'same_source_reachable_entry_count': len(same_source),
                 'same_source_reachable_sample': [row['entry'] for row in same_source[:5]]})
counts = dict(Counter(row['category'] for row in rows))
result = {'schema': 'opencfw-boot-gc-reachability-audit-v1',
          'status': 'PASS_BOUNDED_GC_NATIVE_LEAD_CLASSIFICATION',
          'stock_sha256': R['original_sha256'],
          'placement_sha256': hashlib.sha256(args.placement.read_bytes()).hexdigest(),
          'inventory_sha256': hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
          'crosswalk_sha256': hashlib.sha256(CROSSWALK.read_bytes()).hexdigest(),
          'reachability_sha256': hashlib.sha256(REACH.read_bytes()).hexdigest(),
          'manual_bindings_sha256': hashlib.sha256(MANUAL.read_bytes()).hexdigest(),
          'reviewed_paths_sha256': hashlib.sha256(REVIEWED.read_bytes()).hexdigest(),
          'unretained_selected_symbols': len(rows), 'reachable_native_catalogue_entries': len(reachable),
          'category_counts': counts, 'rows': rows,
          'limits': ['Historical reviewed call-path explanations are leads; this run does not re-execute their behavior against current compiled code.',
                     'A source-file lead does not identify which function within that file the native entry represents.',
                     'This direct-call graph omits possible indirect calls, dynamic dispatch and external ROM behavior.',
                     'Garbage collection of a selected symbol is not by itself a missing-source or runtime failure.']}
args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], counts)
