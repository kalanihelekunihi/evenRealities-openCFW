# SPDX-License-Identifier: MIT
"""Export qualified source for the two-channel context lookup."""
import json
import shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT, sha
from verify_gx8002_logging import check_paths
from verify_gx8002_channel_lookup import verify as replay


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    checks = replay()
    candidate = checks['candidate']
    if not candidate['fits'] or candidate['compiled_sha256'] != candidate['stock_sha256']:
        raise ValueError('Channel lookup source identity changed')
    row = {k: candidate[k] for k in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
    row['stock_occurrences'] = [{'symbol': candidate['symbol'], 'package_offset': 0x1104c,
        'bytes': 28, 'sha256': candidate['stock_sha256'], 'region': 'image_a_xip_text'}]
    if output:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/channel-lookup-candidate.elf', output/'channel-lookup.elf')
    names = ('verify_gx8002_channel_lookup_source.py', 'verify_gx8002_channel_lookup.py',
             'build_gx8002_channel_lookup_candidate.py', 'verify_gx8002_memcpy_source.py')
    return {'functions': [row], 'checks': checks,
            'evidence_sha256': {name: sha((ROOT/'tools'/name).read_bytes()) for name in names},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Byte-identical same-entry lookup admission. Context structures remain stock; their lifecycle, other callers and physical hardware are not qualified.']}

if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-channel-lookup-source-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Channel lookup source admission verified')
