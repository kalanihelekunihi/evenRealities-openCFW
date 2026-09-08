#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for decoded flash otp-read wrapper."""
import contextlib
import io
import json
import shutil
import hashlib
from verify_gx8002_otp_receive_step import verify as verify_step
from compare_gx8002_flash_otp_read import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):
        comparison=compare()
        loop=verify_step()
    evidence={'build':comparison['build'],'comparison':comparison,'loop':loop,
              'loop_argument_sha256':hashlib.sha256((ROOT/'docs/research/gx8002-otp-receive-loop-argument.md').read_bytes()).hexdigest()}
    if not all(row['fits'] for row in evidence['build']['functions']):
        raise ValueError('otp-read envelope exceeded')
    functions=[]
    for row in evidence['build']['functions']:
        functions.append({'symbol':row['symbol'],'section_name':row['section'],
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],
                                                'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                                                'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/otp-read.elf',output/'otp-read.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Full decoded finite traces plus pinned receive-loop structure and reviewed counter argument for summarized large transfers. Candidate frame48 bytes versus stock52. Helpers modeled; synthetic buffers, physical OTP and hardware timing remain unqualified. Oversized prefix domains beyond finite model limits are not independently exercised.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-otp-read-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
