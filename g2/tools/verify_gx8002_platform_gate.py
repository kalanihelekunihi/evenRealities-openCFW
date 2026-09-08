#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission of upstream gate code and compiler-generated switch targets."""
import contextlib
import io
import json
import shutil
from compare_gx8002_platform_gate import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=compare()
    functions=[]
    for row in evidence['placement']['sections']:
        data=row['section'].startswith('.rodata.')
        symbol='open_cfw_gx8002_platform_gate_switches' if data else 'open_cfw_gx8002_platform_gate'
        functions.append({'symbol':symbol,'section_name':row['section'],
                          'ownership_kind':'generated_source_data' if data else 'compiled_c',
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':symbol,'package_offset':row['package_offset'],
                          'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                          'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-platform-gate/gate-fit.elf',output/'gate.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite MMIO comparison with separately qualified lookup modeled.',
                      'Only gate code and generated switch targets selected; other ELF sections excluded.',
                      'Concurrent mutation, timing, and hardware operation remain unqualified.']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
