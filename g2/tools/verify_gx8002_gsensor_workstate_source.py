# SPDX-License-Identifier: MIT
"""Qualify the sensor state reader without claiming closure of its producers."""
import json
import shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT, sha
from verify_gx8002_logging import check_paths
from verify_gx8002_gsensor_workstate import verify as core
from verify_gx8002_gsensor_workstate_printf import verify as printing
from analyze_gx8002_gsensor_state_references import analyze as mapping
from verify_gx8002_board_pin_initialize_source import verify as helper_dependency


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    dependency = helper_dependency()
    checks = {'core': core(), 'printf': printing()}
    state = mapping()
    candidate = checks['core']['candidate']
    if not candidate['fits'] or checks['printf']['candidate'] != candidate:
        raise ValueError('Gsensor candidate changed across qualifications')
    if not state['candidate_data_mapping']['section_mapping_verified_here']:
        raise ValueError('Gsensor initialized-data mapping missing')
    row = {key: candidate[key] for key in ('symbol', 'section_name', 'compiled_bytes', 'compiled_sha256')}
    row['stock_occurrences'] = [{'symbol': candidate['symbol'], 'package_offset': 0xfe94,
                                'bytes': 24, 'sha256': candidate['stock_sha256'],
                                'region': 'image_a_xip_text'}]
    names = ('verify_gx8002_gsensor_workstate_source.py',
             'build_gx8002_gsensor_workstate_candidate.py',
             'verify_gx8002_gsensor_workstate.py',
             'verify_gx8002_gsensor_workstate_printf.py',
             'verify_gx8002_gsensor_workstate_format.py',
             'verify_gx8002_gsensor_workstate_message.py',
             'analyze_gx8002_gsensor_state_references.py',
             'analyze_g2_codec_stage2_sections.py')
    if output:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/gsensor-workstate-candidate.elf',
                        output/'gsensor-workstate.elf')
    return {'functions': [row], 'checks': checks, 'state_mapping': state,
            'helper_dependency': dependency,
            'evidence_sha256': {name: sha((ROOT/'tools'/name).read_bytes()) for name in names},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Finite same-entry reader admission only. Two volatile reads bracket the decoded diagnostic call; helper frames are separate and UART MMIO scripted. State producers, concurrency, whole-device execution and physical hardware remain unqualified. Initialized state data remains retained stock.']}


if __name__ == '__main__':
    report = verify()
    (ROOT/'docs/research/gx8002-gsensor-workstate-source-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Gsensor reader source qualification passed')
