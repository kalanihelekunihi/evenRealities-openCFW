# SPDX-License-Identifier: MIT
"""Qualify upstream decoder initial state for source-data replacement."""
import json, re, shutil
from build_gx8002_decoder_default import ROOT, sha, Elf32
ROWS=(('decoder_state',0x18d40,4),)
from verify_gx8002_decoder_default_startup import verify as startup
from verify_gx8002_decoder_default_consumer import verify as consumer
from verify_gx8002_logging import check_paths


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = {'startup':startup(),'consumer':consumer()}
    path = ROOT / 'build/gx8002-decoder-default/defaults.elf'
    elf = Elf32(path.read_bytes(), 'decoder state')
    rows = []
    symbols = {'decoder_state':'open_cfw_gx8002_max_decoder_state'}
    for name, offset, size in ROWS:
        section = next(s for s in elf.sections if s['name'] == '.' + name)
        symbol = next(s for s in elf.symbols() if s['name'] == symbols[name])
        assert symbol['value'] == section['address'] and symbol['size'] == size
        body = elf.contents(section)
        rows.append({'symbol': symbols[name], 'section_name': '.' + name,
                     'ownership_kind': 'generated_source_data', 'compiled_bytes': size,
                     'compiled_sha256': sha(body), 'stock_occurrences': [
                         {'symbol': symbols[name], 'package_offset': offset, 'bytes': size,
                          'sha256': sha(body), 'region': 'image_a_sram_data'}]})
    registry = (ROOT / 'tools/build_gx8002_source_candidate.py').read_text()
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'", registry))):
        if name == 'gx8002-decoder-default-source-verification.json':
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
        shutil.copyfile(path, output / 'defaults.elf')
    files = ('build_gx8002_decoder_default.py','verify_gx8002_decoder_default_startup.py','verify_gx8002_decoder_default_consumer.py','verify_gx8002_decoder_default_source.py','execute_gx8002_max_decoder.py','verify_gx8002_memcpy_source.py','verify_gx8002_uart_loader_setup.py','compare_gx8002_clear_bss.py','verify_gx8002_power_initialize.py','analyze_gx8002_gsensor_state_references.py','analyze_gx8002_upstream_objects.py','build_transparent_image.py')
    return {'functions': rows, 'evidence': evidence,
            'evidence_sha256': {name: sha((ROOT / 'tools' / name).read_bytes()) for name in files},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Upstream active-state enum initializes compatible int storage at its original address. Startup, decoder consumers and nonoverlap checked; hardware helpers remain modeled.',
                       'Experimental hybrid replacement; complete firmware and physical hardware execution remain unqualified.']}


if __name__ == '__main__':
    result = verify()
    assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-decoder-default-source-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Decoder default source-data qualification passed: 4 bytes')
