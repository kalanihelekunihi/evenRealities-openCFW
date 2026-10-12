#!/usr/bin/env python3
"""Map native image-A XIP function slots to compiled C-SKY function sections.

This is a necessary-size/identity audit, not a final link or equivalence proof.
"""
import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBJECT = ROOT / ('g2/build/c-firmware/20261011/codec-placement-gated-round/'
                 'codec/candidate.o')
NATIVE = ROOT / ('g2/research/corpus/codec/ghidra/open-2026-09-29/'
                 'image_a_xip/functions-000.jsonl')
BINDINGS = HERE / 'resident-other-regions-census.json'
GAPS = HERE / 'xip-function-range-gap-receipt.json'
READELF = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/tools/'
                  'csky-binutils-001/install/bin/csky-elfabiv2-readelf')
CODE_END = 0x1020a8aa

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def readelf(object_path, *args):
    return subprocess.run([str(READELF), *args, str(object_path)],
                          check=True, capture_output=True, text=True).stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=OBJECT)
    parser.add_argument('--output', type=Path,
                        default=HERE/'xip-link-eligibility-manifest.json')
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    assert candidate.is_file() and candidate.is_relative_to(ROOT)
    destination = args.output.resolve()
    assert destination.is_relative_to(ROOT)
    native = sorted((json.loads(line) for line in NATIVE.read_text().splitlines()
                     if int(json.loads(line)['entry'], 16) < CODE_END),
                    key=lambda row: int(row['entry'], 16))
    binding_doc = json.loads(BINDINGS.read_text())['image_a_xip']
    bindings = {row['entry']: row for row in binding_doc['bindings']}
    sections = {}
    for line in readelf(candidate, '-SW').splitlines():
        match = re.search(r'\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+'
                          r'([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)', line)
        if match:
            sections[int(match.group(1))] = {
                'name': match.group(2), 'type': match.group(3),
                'bytes': int(match.group(5), 16)}
    by_address = {}
    for line in readelf(candidate, '-sW').splitlines():
        parts = line.split()
        if len(parts) < 8 or parts[3] != 'FUNC' or parts[4] not in ('GLOBAL', 'WEAK'):
            continue
        match = re.search(r'_([0-9a-f]{8})$', parts[-1])
        if not match or not match.group(1).startswith('1020'):
            continue
        ndx = int(parts[6]) if parts[6].isdigit() else None
        symbol = {'name': parts[-1], 'compiled_bytes': int(parts[2]),
                  'section': sections[ndx]['name'] if ndx in sections else None,
                  'section_bytes': sections[ndx]['bytes'] if ndx in sections else None,
                  'section_index': ndx, 'section_offset': int(parts[1], 16)}
        by_address.setdefault(match.group(1), []).append(symbol)
    relocations = {}
    relocation_entries = {}
    current_relocation_section = None
    for line in readelf(candidate, '-rW').splitlines():
        match = re.match(r"Relocation section '([^']+)' .* contains (\d+) entries?:", line)
        if match:
            current_relocation_section = match.group(1)
            relocations[current_relocation_section] = int(match.group(2))
            relocation_entries[current_relocation_section] = []
            continue
        parts = line.split()
        if (current_relocation_section and len(parts) >= 5
                and re.fullmatch(r'[0-9a-f]{8}', parts[0])
                and parts[2].startswith('R_CKCORE_')):
            relocation_entries[current_relocation_section].append({
                'section_offset': '0x' + parts[0],
                'kind': parts[2],
                'target': parts[4],
                'addend': ' '.join(parts[5:]),
            })
    rows = []
    for i, row in enumerate(native):
        address = int(row['entry'], 16)
        next_address = (int(native[i+1]['entry'], 16)
                        if i+1 < len(native) else CODE_END)
        symbols = by_address.get(row['entry'], [])
        item = {'entry': '0x' + row['entry'], 'native_name': row['name'],
                'native_ranges_inclusive': row['ranges'],
                'native_body_bytes': row['body_bytes'],
                'native_body_sha256': row['body_sha256'],
                'next_catalogue_entry': hex(next_address),
                'fixed_start_slot_bytes': next_address-address,
                'source_binding': bindings.get(row['entry']),
                'direct_symbols': symbols}
        if len(symbols) == 1:
            symbol = symbols[0]
            reloc = '.rela' + symbol['section'] if symbol['section'] else None
            item['compiled_section_relocations'] = relocations.get(reloc, 0)
            item['compiled_section_relocation_entries'] = relocation_entries.get(reloc, [])
            size = symbol['compiled_bytes']
            item['fixed_start_size_fit'] = size <= next_address-address
            item['excess_bytes_if_fixed'] = max(0, size-(next_address-address))
            section_size = symbol['section_bytes']
            item['fixed_section_size_fit'] = (
                symbol['section_offset'] == 0 and section_size is not None
                and section_size <= next_address-address)
            item['excess_section_bytes_if_fixed'] = (
                max(0, section_size-(next_address-address))
                if section_size is not None else None)
            item['size_relation_to_native_body'] = ('equal' if size == row['body_bytes']
                else 'larger' if size > row['body_bytes'] else 'smaller')
            item['section_isolated_to_symbol'] = (
                symbol['section_offset'] == 0 and
                symbol['section_bytes'] == size)
            item['placement_status'] = (
                'section_slot_overflow' if not item['fixed_section_size_fit']
                else 'section_size_only_eligible')
        else:
            item['placement_status'] = ('no_direct_named_symbol' if not symbols
                                        else 'ambiguous_direct_symbols')
        rows.append(item)
    counts = Counter(row['placement_status'] for row in rows)
    gap_doc = json.loads(GAPS.read_text())
    report = {
        'candidate_object': str(candidate.relative_to(ROOT)),
        'candidate_sha256': sha(candidate),
        'native_catalogue_sha256': sha(NATIVE),
        'binding_catalogue_sha256': sha(BINDINGS),
        'native_gap_receipt_sha256': sha(GAPS),
        'native_code_span': ['0x10203004', hex(CODE_END)],
        'native_code_span_bytes': CODE_END-0x10203004,
        'native_label_count_before_data_tail': len(native),
        'source_candidate_bindings': len(bindings),
        'status_counts': dict(counts),
        'fixed_address_section_overflow_bytes_sum': sum(
            row.get('excess_section_bytes_if_fixed') or 0 for row in rows),
        'compiled_direct_section_bytes_sum': sum(
            row['direct_symbols'][0]['section_bytes'] for row in rows
            if len(row['direct_symbols']) == 1),
        'compiled_direct_section_relocations': sum(
            row.get('compiled_section_relocations', 0) for row in rows),
        'native_catalogue_gap_count': gap_doc['gap_count'],
        'native_catalogue_gap_bytes': gap_doc['gap_bytes'],
        'native_named_ranges_without_fixed_section_eligibility': [
            {'entry': row['entry'], 'native_ranges_inclusive': row['native_ranges_inclusive'],
             'reason': row['placement_status'],
             'compiled_section_bytes': (row['direct_symbols'][0]['section_bytes']
                                        if len(row['direct_symbols']) == 1 else None),
             'slot_bytes': row['fixed_start_slot_bytes']}
            for row in rows if row['placement_status'] != 'section_size_only_eligible'],
        'unplaced_native_gap_ranges': gap_doc['gaps'],
        'native_function_slots': rows,
        'limits': [
            'Size fit is necessary but does not prove correct code, branch reach, '
            'literal pools, relocations, final address assignment, or runtime behavior.',
            'Native body labels may include interior or data aliases; missing direct '
            'symbol does not alone mean missing C source.',
            'Candidate compiled size includes only the named function symbol; helpers '
            'and associated data may need additional placement.',
        ],
    }
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status_counts': dict(counts),
                      'gap_count': gap_doc['gap_count'],
                      'gap_bytes': gap_doc['gap_bytes'],
                      'output': str(destination.relative_to(ROOT))}))

if __name__ == '__main__':
    main()
