#!/usr/bin/env python3
"""Select -Os C units that eliminate XIP overflows without new slot regressions."""
import json
from collections import defaultdict
from pathlib import Path
from probe_xip_overflow_os import OUT, section_sizes

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE/'xip-link-eligibility-manifest.json').read_text())
PROBE = json.loads((OUT/'receipt.json').read_text())
sources = sorted({row['source'] for row in PROBE['rows']})
objects = {source: section_sizes(OUT/f'file-{i:03d}.o')
           for i, source in enumerate(sources)}
results = defaultdict(lambda: {'newly_fitting_entries': [],
                               'new_overflow_entries': [],
                               'still_overflow_entries': []})
for native in MANIFEST['native_function_slots']:
    binding = native['source_binding']
    if not binding or binding['candidate_source'] not in objects:
        continue
    if len(native['direct_symbols']) != 1:
        continue
    source = binding['candidate_source']
    symbol = native['direct_symbols'][0]['name']
    current = objects[source].get(symbol)
    assert current is not None, (source, symbol)
    fits = current['section_bytes'] <= native['fixed_start_slot_bytes']
    if native['placement_status'] == 'section_slot_overflow':
        key = 'newly_fitting_entries' if fits else 'still_overflow_entries'
        results[source][key].append(native['entry'])
    elif not fits:
        results[source]['new_overflow_entries'].append(native['entry'])
qualified = {source: results[source] for source in sources
             if results[source]['newly_fitting_entries']
             and not results[source]['new_overflow_entries']}
probed_hashes = {row['source']: row['source_sha256'] for row in PROBE['rows']}
for source, record in qualified.items():
    record['probed_source_sha256'] = probed_hashes[source]
assert len(qualified) == 35
assert sum(len(x['newly_fitting_entries']) for x in qualified.values()) == 51
policy = {
    'baseline_candidate_sha256': MANIFEST['candidate_sha256'],
    'optimization': '-Os',
    'source_probe_receipt': 'xip-size-probe/all-os/receipt.json',
    'qualification': 'target C-SKY section sizes for every direct native-bound function in each selected source file; semantic/runtime equality remains unqualified',
    'qualified_files': qualified,
    'qualified_file_count': len(qualified),
    'newly_fitting_native_slots': 51,
    'remaining_baseline_section_overflows': 113 - 51,
}
(HERE/'xip-os-qualified-sources.json').write_text(json.dumps(policy, indent=2)+'\n')
print(json.dumps({'files':len(qualified),'newly_fitting_slots':51,
                  'remaining_baseline_overflows':62}))
