# SPDX-License-Identifier: MIT
"""Audit matched public audio wrappers against registered source ownership.

Literal scans are evidence of stored addresses, not exhaustive pointer-use or
reachability analysis. Unmatched SDK routines remain unresolved.
"""
import json, re, struct
from analyze_gx8002_audio_output_public import analyze, ROOT, IMAGE, sha

def analyze_coverage():
    identities = analyze()
    registry = (ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    admissions = []
    evidence = {}
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'", registry))):
        path = ROOT/'docs/research'/name
        if not path.exists():
            continue
        report = json.loads(path.read_text())
        for row in report.get('functions', [report]):
            for occurrence in row.get('stock_occurrences', row.get('exact_stock_occurrences', [])):
                admissions.append((name, row, occurrence))
    matched, unresolved = [], []
    for function in identities['functions']:
        if not function['matches']:
            unresolved.append(function['section'])
            continue
        for match in function['matches']:
            owners = [(n, r, o) for n, r, o in admissions
                      if o['package_offset'] == match['package_offset']
                      and o['bytes'] == function['bytes']
                      and r.get('ownership_kind', 'compiled_c') == 'compiled_c']
            if len(owners) != 1:
                raise ValueError(('Matched wrapper source ownership', function['section'], len(owners)))
            name, row, occurrence = owners[0]
            if occurrence['sha256'] != match['stock_sha256']:
                raise ValueError('Wrapper stock identity differs')
            evidence[name] = sha((ROOT/'docs/research'/name).read_bytes())
            matched.append({'upstream_section': function['section'],
                            'package_offset': match['package_offset'],
                            'envelope_bytes': function['bytes'],
                            'source_symbol': row['symbol'],
                            'compiled_bytes': row['compiled_bytes'],
                            'admission': name})
    stock = IMAGE.read_bytes()
    pointer = struct.pack('<I', 0x2002734c)
    literals = []
    for offset in range(len(stock)-3):
        if stock[offset:offset+4] != pointer:
            continue
        owners = [r['upstream_section'] for r in matched
                  if r['package_offset'] <= offset and offset+4 <= r['package_offset']+r['envelope_bytes']]
        literals.append({'package_offset': offset, 'matched_wrapper_owners': owners})
    return {'stock_sha256': identities['stock_sha256'],
            'sdk_commit': identities['sdk_commit'], 'oracle': identities['oracle'],
            'matched_source_wrappers': matched, 'unresolved_sdk_sections': unresolved,
            'dispatch_pointer_literal_occurrences': literals,
            'admission_sha256': evidence,
            'source_only': False, 'hardware_qualified': False,
            'limits': ['Ownership audit uses registered reviewed reports; does not rerun their behavioral verification.',
                       'Unmatched SDK sections may be absent or compiled differently; no absence claim.',
                       'Literal scan does not cover computed pointers, aliases or runtime writes.',
                       'Global BSS initialization, startup copying and full-firmware closure remain unresolved.']}

if __name__ == '__main__':
    report = analyze_coverage()
    (ROOT/'docs/research/gx8002-audio-output-public-coverage.json').write_text(json.dumps(report, indent=2)+'\n')
    print(len(report['matched_source_wrappers']), 'matched source wrappers;', len(report['unresolved_sdk_sections']), 'unresolved SDK sections')
