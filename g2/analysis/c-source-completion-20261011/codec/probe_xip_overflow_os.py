#!/usr/bin/env python3
"""Recompile only source files with XIP section overflows under target -Os."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUILD = ROOT/'g2/build/c-firmware/20261011/codec-placement-gated-round/receipt.json'
MANIFEST = HERE/'xip-link-eligibility-manifest.json'
OUT = HERE/'xip-size-probe/all-os'
READELF = ROOT/('g2/build/pseudocode-first/20260930T190500Z/tools/'
                'csky-binutils-001/install/bin/csky-elfabiv2-readelf')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def section_sizes(obj):
    listing = subprocess.run([str(READELF), '-SW', str(obj)],
                             check=True, capture_output=True, text=True).stdout
    sections = {}
    for line in listing.splitlines():
        m = re.search(r'\[\s*(\d+)\]\s+(\S+)\s+PROGBITS\s+'
                      r'[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)', line)
        if m:
            sections[int(m.group(1))] = (m.group(2), int(m.group(3), 16))
    symbols = subprocess.run([str(READELF), '-sW', str(obj)],
                             check=True, capture_output=True, text=True).stdout
    result = {}
    for line in symbols.splitlines():
        p = line.split()
        if (len(p) >= 8 and p[3] == 'FUNC' and p[6].isdigit()
                and int(p[6]) in sections):
            result[p[-1]] = {'function_bytes': int(p[2]),
                             'section': sections[int(p[6])][0],
                             'section_bytes': sections[int(p[6])][1]}
    return result

def main():
    manifest = json.loads(MANIFEST.read_text())
    build = json.loads(BUILD.read_text())['images']['codec']
    assert build['candidate_compilation_passed'] and build['source_snapshot_coherent_at_link']
    assert build['output_sha256'] == manifest['candidate_sha256']
    overflow = [r for r in manifest['native_function_slots']
                if r['placement_status'] == 'section_slot_overflow']
    sources = sorted({r['source_binding']['candidate_source'] for r in overflow})
    commands = {}
    for entry in build['build_commands']:
        argv = entry['argv']
        if '-c' in argv:
            src = argv[argv.index('-c')+1]
            if src.startswith('/repo/'):
                commands[src.removeprefix('/repo/')] = argv
    OUT.mkdir(parents=True, exist_ok=True)
    objects = {}
    for i, source in enumerate(sources):
        argv = commands[source].copy()
        assert '-O2' in argv
        argv[argv.index('-O2')] = '-Os'
        output_mount = next(j for j, value in enumerate(argv)
                            if value.endswith('dst=/out'))
        argv[output_mount] = f'type=bind,src={OUT},dst=/out'
        obj = OUT/f'file-{i:03d}.o'
        argv[argv.index('-o')+1] = '/out/'+obj.name
        subprocess.run(argv, check=True, capture_output=True, text=True)
        objects[source] = {'object_sha256': sha(obj),
                           'symbols': section_sizes(obj)}
    rows = []
    for native in overflow:
        symbol = native['direct_symbols'][0]['name']
        source = native['source_binding']['candidate_source']
        current = objects[source]['symbols'].get(symbol)
        assert current is not None, (source, symbol)
        rows.append({'entry': native['entry'], 'source': source,
                     'source_sha256': sha(ROOT/source), 'symbol': symbol,
                     'native_slot_bytes': native['fixed_start_slot_bytes'],
                     'O2_section_bytes': native['direct_symbols'][0]['section_bytes'],
                     'Os_section_bytes': current['section_bytes'],
                     'Os_section_fits_slot': (current['section_bytes'] <=
                                              native['fixed_start_slot_bytes']),
                     'Os_section_reduction_bytes': (
                         native['direct_symbols'][0]['section_bytes']-
                         current['section_bytes'])})
    counts = Counter('fits' if r['Os_section_fits_slot'] else 'still_overflows'
                     for r in rows)
    receipt = {'candidate_sha256': manifest['candidate_sha256'],
               'compiler_target': 'csky-abiv2-elf-gcc -mcpu=ck804ef -mhard-float',
               'compiled_source_files': len(sources),
               'overflows_tested': len(rows), 'Os_status_counts': dict(counts),
               'rows': rows,
               'scope': 'isolated -Os section size only; no function/native behavior or final relocation qualification'}
    (OUT/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'sources': len(sources), 'overflows': len(rows),
                      'status': dict(counts)}))

if __name__ == '__main__':
    main()
