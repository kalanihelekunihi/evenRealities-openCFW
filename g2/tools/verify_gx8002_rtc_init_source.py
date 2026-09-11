# SPDX-License-Identifier: MIT
"""Aggregate RTC initializer source qualification and export."""
import json
import shutil
from pathlib import Path
from verify_gx8002_rtc_init import verify as core,ROOT
from analyze_gx8002_rtc_init import analyze
from verify_gx8002_rtc_init_gate_composition import verify as gate
from verify_gx8002_rtc_init_start_composition import verify as start
from verify_gx8002_rtc_clock_composition import verify as clock
from verify_gx8002_rtc_irq_composition import verify as irq
from verify_gx8002_rtc_printf_composition import verify as printf
from verify_gx8002_clock_frequency_source import verify as refresh_clock
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    dependencies=refresh_clock()
    checks={'upstream':analyze(),'core':core(),'gate':gate(),'start':start(),'clock':clock(),'irq':irq(),'printf':printf()}
    candidate=checks['core']['candidate']
    if not candidate['fits']:raise ValueError('RTC initializer envelope')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfc48,'bytes':72,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_rtc_init_source.py','verify_gx8002_rtc_init.py','build_gx8002_rtc_init_candidate.py',
        'analyze_gx8002_rtc_init.py','verify_gx8002_rtc_init_gate_composition.py','verify_gx8002_rtc_init_start_composition.py',
        'verify_gx8002_rtc_clock_composition.py','verify_gx8002_rtc_irq_composition.py','verify_gx8002_rtc_printf_composition.py',
        'verify_gx8002_rtc_diagnostic_format.py','compare_gx8002_irq.py','compare_gx8002_printf_abi.py',
        'compare_gx8002_format.py','verify_gx8002_memcpy_source.py','build_gx8002_rtc_start_tick_candidate.py')
    pins={name:sha((ROOT/'tools'/name).read_bytes()) for name in names}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/rtc-init-candidate.elf',output/'rtc-init.elf')
    return {'functions':[row],'checks':checks,'clock_dependency':dependencies,'evidence_sha256':pins,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite initializer and separate helper compositions. Shared whole-device timing, physical UART and RTC IRQ delivery not qualified. Experimental source admission within this finite scope.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-init-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('RTC initializer aggregate passed')
