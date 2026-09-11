# SPDX-License-Identifier: MIT
"""Aggregate finite board initializer source qualification and export."""
import json,shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_board_pin_initialize import verify as core
from verify_gx8002_board_pin_initialize_table import verify as table
from verify_gx8002_board_pin_initialize_gpio import verify as gpio
from verify_gx8002_board_pin_initialize_check import verify as checker
from verify_gx8002_board_pin_initialize_padmux import verify as padmux
from verify_gx8002_board_pin_initialize_setup import verify as setup
from verify_gx8002_board_pin_initialize_printf import verify as printing
from verify_gx8002_board_pin_setup_source import verify as setup_dependency


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    dependency=setup_dependency()
    checks={'core':core(),'table':table(),'gpio':gpio(),'checker':checker(),
            'padmux':padmux(),'setup':setup(),'printf':printing()}
    candidate=checks['core']['candidate']
    if not candidate['fits'] or any(x['candidate']!=candidate for x in checks.values()):
        raise ValueError('Board initializer candidate changed')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfe2c,'bytes':104,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_board_pin_initialize_source.py','build_gx8002_board_pin_initialize_candidate.py',
           'verify_gx8002_board_pin_initialize.py','verify_gx8002_board_pin_initialize_table.py',
           'verify_gx8002_board_pin_initialize_gpio.py','verify_gx8002_board_pin_initialize_check.py',
           'verify_gx8002_board_pin_initialize_padmux.py','verify_gx8002_board_pin_initialize_setup.py',
           'verify_gx8002_board_pin_initialize_printf.py','verify_gx8002_board_pin_initialize_error.py',
           'verify_gx8002_board_pin_initialize_diagnostic_format.py','verify_gx8002_board_pin_defaults.py',
           'verify_gx8002_gpio_output.py','build_gx8002_gpio_output_candidate.py')
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/board-pin-initialize-candidate.elf',output/'board-pin-initialize.elf')
    return {'functions':[row],'checks':checks,'setup_dependency':dependency,
            'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in names},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite experimental same-entry initializer admission. Separate helper frames and scripted MMIO; some setter checker returns modeled in initialization composition. Whole-device nested execution, concurrency and physical hardware remain unqualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-initialize-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board initializer aggregate passed')
