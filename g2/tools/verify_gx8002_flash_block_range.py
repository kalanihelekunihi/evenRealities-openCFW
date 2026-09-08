#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for decoded flash block-range wrapper."""
import contextlib
import io
import json
import shutil
from compare_gx8002_flash_block_bounds import verify as compare
from compare_gx8002_flash_block_wrapper import verify as compare_wrapper
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):
        comparison=compare()
        wrapper=compare_wrapper()
    evidence={'build':comparison['build'],'comparison':comparison,'wrapper':wrapper}
    if not all(row['fits'] for row in evidence['build']['functions']):
        raise ValueError('block-range envelope exceeded')
    if not evidence['build']['functions'][2]['byte_exact']:
        raise ValueError('sync differs from reviewed push/call/pop stock sequence')
    functions=[]
    for row in evidence['build']['functions']:
        functions.append({'symbol':row['symbol'],'section_name':row['section'],
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],
                                                'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                                                'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/block-range.elf',output/'block-range.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Qualified block selection, output/state alias ordering, wrapper calls and stack; sync is byte-exact push/call wait-ready/pop. Physical flash remains unqualified.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-block-range-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
