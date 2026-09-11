# SPDX-License-Identifier: MIT
"""Aggregate finite board pin guard source admission and artifact export."""
import json
import shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_board_pin_configure import verify as core
from verify_gx8002_board_pin_padmux_composition import verify as padmux
from verify_gx8002_board_pin_printf_composition import verify as printing
from verify_gx8002_putf_boundary import verify as putf
from verify_gx8002_fputc_boundary import verify as fputc
from verify_gx8002_console_boundary import verify as console


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'core':core(),'padmux':padmux(),'printf':printing(),'putf':putf(),'fputc':fputc(),'console':console()}
    candidate=checks['core']['candidate']
    if not candidate['fits'] or candidate!=checks['padmux']['candidate'] or candidate!=checks['printf']['candidate']:
        raise ValueError('Board pin candidate mismatch')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfd68,'bytes':64,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_board_pin_source.py','build_gx8002_board_pin_configure_candidate.py',
           'verify_gx8002_board_pin_configure.py','verify_gx8002_board_pin_padmux_composition.py',
           'verify_gx8002_board_pin_printf_composition.py','verify_gx8002_board_pin_error.py',
           'verify_gx8002_board_pin_diagnostic_format.py','execute_gx8002_format_composed.py',
           'execute_gx8002_padding_composed.py','verify_gx8002_putf_boundary.py',
           'verify_gx8002_fputc_boundary.py','verify_gx8002_console_boundary.py',
           'compare_gx8002_printf_abi.py','compare_gx8002_ui2a.py','compare_gx8002_uart_putc.py',
           'compare_gx8002_uart_transmit.py','verify_gx8002_padmux_set.py',
           'verify_gx8002_padmux_check.py','verify_gx8002_padmux_get.py','verify_gx8002_memcpy_source.py')
    pins={name:sha((ROOT/'tools'/name).read_bytes()) for name in names}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/board-pin-configure-candidate.elf',output/'board-pin.elf')
    return {'functions':[row],'checks':checks,'evidence_sha256':pins,'source_admitted':True,
            'hardware_qualified':False,'limits':['Finite experimental guard admission. Separate helper frames, translated buffers, selected console port zero and scripted UART MMIO. Initialization lifecycle, shared nested stack, concurrency and physical hardware not qualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Board pin source aggregate passed')
