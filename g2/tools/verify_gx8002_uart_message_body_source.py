# SPDX-License-Identifier: MIT
"""Admit reconstructed UART message body sender."""
import json,shutil
from verify_gx8002_uart_send_body_complete import verify as core,ROOT,sha
from verify_gx8002_uart_send_body_mutations import verify as mutation_checks
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=core();evidence["mutation_checks"]=mutation_checks();functions=[]
    for candidate in evidence['candidate']['functions']:
        if not candidate['fits']:raise ValueError('Initialization envelope')
        row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        if 'ownership_kind' in candidate:row['ownership_kind']=candidate['ownership_kind']
        row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':candidate['package_offset'],
          'bytes':candidate['stock_envelope_bytes'],'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
        functions.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-uart-message-body/buffers.elf',output/'buffers.elf')
    files=('verify_gx8002_uart_message_body_source.py','verify_gx8002_uart_send_body_complete.py','verify_gx8002_uart_send_body_mutations.py','build_gx8002_uart_message_body.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
      'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},
      'limits':['Complete decoded stock/source and independent baseline oracle, mutation, alias and null checks pass. Valid ports0/1; helpers modeled. Null packet with zero sent preserves observed unmapped length read. Physical UART, arbitrary concurrency and out-of-range port storage remain unqualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-uart-message-body-source-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('UART body sender source admission passed')
