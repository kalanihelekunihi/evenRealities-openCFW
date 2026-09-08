#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for decoded SPI transport and polling helpers."""
import contextlib
import io
import json
import shutil
from compare_gx8002_spi_read import verify as compare_read
from compare_gx8002_spi_write import verify as compare_write
from compare_gx8002_spi_idle import verify as compare_idle
from compare_gx8002_spi_empty import verify as compare_empty
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):
        reports=[fn() for fn in (compare_read,compare_write,compare_idle,compare_empty)]
    if any(r['build']!=reports[0]['build'] for r in reports):raise ValueError('transport build changed between checks')
    evidence={'build':reports[0]['build'],'comparisons':dict(zip(('read','write','idle','empty'),reports))}
    functions=[]
    for row in evidence['build']['functions']:
        functions.append({'symbol':row['symbol'],'section_name':row['section'],
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],
                                                'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                                                'region':'image_a_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/transport.elf',output/'transport.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Valid nonwrapping caller buffers and polled MMIO behavior; controller limits, readiness liveness and physical hardware remain unqualified.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-transport-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
