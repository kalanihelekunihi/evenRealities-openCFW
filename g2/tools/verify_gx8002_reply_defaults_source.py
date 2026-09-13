# SPDX-License-Identifier: MIT
"""Qualify typed reply packet for source-data replacement."""
import json, re, shutil
from build_gx8002_reply_defaults import ROOT, sha, Elf32
ROWS=(('reply_packet',0x18d70,32),)
from verify_gx8002_reply_defaults_readiness import verify as readiness
from verify_gx8002_logging import check_paths


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    evidence = readiness()
    assert all(row['identical'] for row in evidence['helper_promotion'].values()), 'Helper promotion incomplete'
    for name in ('app_reply','i2s_ack'):
        live=ROOT/'build/gx8002-source-candidate'/name.replace('_','-')/(name.replace('_','-')+'.elf')
        staged=ROOT/'build/gx8002-reply-sdk-types'/(name+'.elf')
        a,b=Elf32(live.read_bytes(),name),Elf32(staged.read_bytes(),name)
        sa=next(s for s in a.sections if s['name']=='.text');sb=next(s for s in b.sections if s['name']=='.text')
        assert sa['address']==sb['address'] and a.contents(sa)==b.contents(sb), 'Registered helper differs'
    path = ROOT / 'build/gx8002-reply-defaults/defaults.elf'
    elf = Elf32(path.read_bytes(), 'decoder state')
    rows = []
    symbols = {'reply_packet':'open_cfw_gx8002_app_reply_state'}
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
        if name == 'gx8002-reply-defaults-source-verification.json':
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
    files = tuple(sorted(p.name for p in (ROOT/'tools').glob('*gx8002*reply*.py'))) + ('verify_gx8002_ack_enqueue_composition.py','verify_gx8002_i2s_ack.py','execute_gx8002_i2s_ack.py','execute_gx8002_uart_message_enqueue.py','verify_gx8002_uart_message_enqueue.py','verify_gx8002_uart_loader_setup.py','compare_gx8002_clear_bss.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions': rows, 'evidence': evidence,
            'evidence_sha256': {name: sha((ROOT / 'tools' / name).read_bytes()) for name in files},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['SDK packet defaults match original storage. Promoted helper source and registered executable identity, type contract, startup, consumer and enqueue composition checked; lower hardware helpers remain modeled.',
                       'Experimental hybrid replacement; complete firmware and physical hardware execution remain unqualified.']}


if __name__ == '__main__':
    result = verify()
    assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-reply-defaults-source-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Reply packet source-data qualification passed: 32 bytes')
