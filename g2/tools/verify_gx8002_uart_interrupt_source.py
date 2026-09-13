# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed UART interrupt handling for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_uart_interrupt_dispatch import verify as core,ROOT,sha
from verify_gx8002_uart_interrupt_buffered import verify as buffered
from verify_gx8002_uart_interrupt_mutation import verify as mutation
from verify_gx8002_uart_interrupt_stall import verify as stalled
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();candidate=qualification['candidate'];item=candidate['functions'][0]
    additional={name:fn() for name,fn in (('buffered',buffered),('mutation',mutation),('stalled',stalled))}
    if any(r['candidate']!=candidate for r in additional.values()):raise ValueError('UART interrupt candidate drift')
    if not item['fits']:raise ValueError('UART interrupt envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-interrupt/interrupt.elf',output/'interrupt.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_uart_interrupt.py','verify_gx8002_uart_interrupt_dispatch.py','verify_gx8002_uart_interrupt_buffered.py','verify_gx8002_uart_interrupt_mutation.py','verify_gx8002_uart_interrupt_stall.py','execute_gx8002_uart_interrupt.py','verify_gx8002_uart_interrupt_source.py','verify_gx8002_memcpy_source.py')}
    return {'functions':[row],'qualification':qualification,'additional_qualification':additional,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded dispatch, bounded buffered transfers, callback-driven descriptor mutation and stalled drain prefixes checked. Callback bodies and MMIO stimuli modeled; arbitrary counts, concurrency and physical interrupt delivery remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-interrupt-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UART interrupt source qualification passed')
