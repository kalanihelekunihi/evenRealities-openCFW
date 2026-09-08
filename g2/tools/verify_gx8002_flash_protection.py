#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for decoded flash protection queries."""
import contextlib
import io
import json
import shutil
from compare_gx8002_flash_protection import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):
        comparison=compare()
    evidence={'build':comparison['build'],'comparison':comparison}
    if not all(row['fits'] for row in evidence['build']['functions']):
        raise ValueError('protection envelope exceeded')
    functions=[]
    for row in evidence['build']['functions']:
        functions.append({'symbol':row['symbol'],'section_name':row['section'],
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],
                                                'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                                                'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/protection.elf',output/'protection.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Qualified ordered query effects and four output aliases; profile initialization and physical hardware remain unqualified. Source includes five explicit CK804 narrow-load instructions.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-protection-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
