# SPDX-License-Identifier: MIT
"""Finite source admission for the recovered eight-pin setup routine."""
import json,shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_board_pin_setup import verify as core
from verify_gx8002_board_pin_setup_guard_composition import verify as guard
from verify_gx8002_board_pin_setup_cleanup import verify as cleanup
from verify_gx8002_board_pin_setup_printf import verify as printing
from verify_gx8002_board_pin_source import verify as guard_dependency


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    dependency=guard_dependency()
    checks={'core':core(),'guard':guard(),'cleanup':cleanup(),'printf':printing()}
    candidate=checks['core']['candidate']
    if not candidate['fits'] or any(x['candidate']!=candidate for x in checks.values()):
        raise ValueError('Setup qualification candidate changed')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfda8,'bytes':132,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_board_pin_setup_source.py','build_gx8002_board_pin_setup_candidate.py',
           'verify_gx8002_board_pin_setup.py','verify_gx8002_board_pin_setup_guard_composition.py',
           'verify_gx8002_board_pin_setup_cleanup.py','verify_gx8002_board_pin_setup_printf.py',
           'verify_gx8002_board_pin_setup_error.py','verify_gx8002_board_pin_setup_diagnostic_format.py')
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/board-pin-setup-candidate.elf',output/'board-pin-setup.elf')
    return {'functions':[row],'checks':checks,'guard_dependency':dependency,
            'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in names},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite experimental same-entry source admission including original fatal self-loop. Separate helper frames and scripted register readback/UART status. Whole-board initialization lifecycle, concurrency and physical hardware remain unqualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-setup-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Eight-pin setup source aggregate passed')
