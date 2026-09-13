# SPDX-License-Identifier: MIT
"""Qualify typed SDK mode descriptors for source-data replacement."""
import json, re, shutil
from build_gx8002_mode_descriptors import ROOT, ROWS, sha, Elf32
from verify_gx8002_mode_descriptor_dispatch import verify as dispatch
from verify_gx8002_logging import check_paths


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = dispatch()
    path = ROOT / 'build/gx8002-mode-descriptors/descriptors.elf'
    elf = Elf32(path.read_bytes(), 'mode descriptors')
    rows = []
    symbols = {'mode_list': 'open_cfw_gx8002_mode_list', 'tws_info': 'lvp_tws_mode_info'}
    for name, offset, size in ROWS:
        section = next(s for s in elf.sections if s['name'] == '.' + name)
        symbol = next(s for s in elf.symbols() if s['name'] == symbols[name])
        assert symbol['value'] == section['address'] and symbol['size'] == size
        body = elf.contents(section)
        rows.append({'symbol': symbols[name], 'section_name': '.' + name,
                     'ownership_kind': 'generated_source_data', 'compiled_bytes': size,
                     'compiled_sha256': sha(body), 'stock_occurrences': [
                         {'symbol': symbols[name], 'package_offset': offset, 'bytes': size,
                          'sha256': sha(body), 'region': 'image_a_xip_text'}]})
    registry = (ROOT / 'tools/build_gx8002_source_candidate.py').read_text()
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'", registry))):
        if name == 'gx8002-mode-descriptors-source-verification.json':
            continue
        report = json.loads((ROOT / 'docs/research' / name).read_text())
        for row in report.get('functions', [report]):
            for occurrence in row.get('stock_occurrences', row.get('exact_stock_occurrences', [])):
                start, size = occurrence.get('package_offset'), occurrence.get('bytes')
                if start is not None and size is not None:
                    assert not any(start < offset + length and offset < start + size
                                   for _, offset, length in ROWS), (name, occurrence)
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, output / 'descriptors.elf')
    files = ('build_gx8002_mode_descriptors.py', 'verify_gx8002_mode_descriptor_bindings.py',
             'verify_gx8002_mode_descriptor_dispatch.py', 'verify_gx8002_mode_descriptors_source.py',
             'compare_gx8002_mode.py', 'verify_gx8002_memcpy_source.py')
    return {'functions': rows, 'evidence': evidence,
            'evidence_sha256': {name: sha((ROOT / 'tools' / name).read_bytes()) for name in files},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Typed upstream SDK descriptors use named, authenticated source-owned references. Original placement and bytes, compiled indirect dispatch and package nonoverlap checked.',
                       'Experimental hybrid replacement; complete firmware and physical hardware execution remain unqualified.']}


if __name__ == '__main__':
    result = verify()
    assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-mode-descriptors-source-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Mode descriptor source-data qualification passed: 28 bytes')
