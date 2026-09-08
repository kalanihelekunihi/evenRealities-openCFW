#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the reviewed dispatcher and C-authored string to the hybrid build."""
import contextlib
import io
import json
import shutil
from compare_gx8002_uart_tick import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=compare()
    rows=[]
    for row in evidence['placement']['sections']:
        is_data=row['section'].startswith('.rodata')
        symbol='open_cfw_gx8002_uart_error_string' if is_data else 'open_cfw_gx8002_uart_async_tick'
        rows.append({'symbol':symbol,'section_name':row['section'],
                     'ownership_kind':'generated_source_data' if is_data else 'compiled_c',
                     'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                     'stock_occurrences':[{'symbol':symbol,'package_offset':row['package_offset'],
                     'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                     'region':'image_a_xip_data' if is_data else 'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-uart-tick/tick.elf',output/'tick.elf')
    return {'functions':rows,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Experimental same-entry hybrid; finite modeled dependency comparison.',
                      'Queue/registration storage remains retained; device timing unqualified.']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
