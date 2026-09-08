#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit only the qualified upstream clock lookup and source-defined tables."""
import contextlib
import io
import json
import shutil
from compare_gx8002_clock_lookup import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()): evidence=compare()
    lookup=evidence['evidence']['module_lookup']
    functions=[{'symbol':'__module_get_info','compiled_bytes':lookup['compiled_bytes'],
                'compiled_sha256':lookup['compiled_sha256'],'stock_occurrences':[{
                'symbol':'__module_get_info','package_offset':lookup['package_offset'],
                'bytes':lookup['stock_envelope_bytes'],'sha256':lookup['stock_sha256'],
                'region':'image_a_sram_text'}]}]
    for row in evidence['evidence']['tables']:
        functions.append({'symbol':row['symbol'],'section_name':row['section_name'],
                          'ownership_kind':'generated_source_data','compiled_bytes':row['bytes'],
                          'compiled_sha256':row['sha256'],'stock_occurrences':[{
                          'symbol':row['symbol'],'package_offset':row['package_offset'],
                          'bytes':row['bytes'],'sha256':row['sha256'],'region':'image_a_sram_data'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-platform-gate/tables.elf',output/'tables.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Only lookup and three data sections admitted; analysis gate and wrapper excluded.',
                      'No concurrent table mutation, overlapping output, or hardware/timing qualification.',
                      'One table-alignment byte and remaining clock code are retained.']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
