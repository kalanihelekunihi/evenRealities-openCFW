#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for reviewed power registration routines."""
import contextlib
import io
import json
import shutil
from compare_gx8002_power_registration import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=compare()
    functions=[]
    for row in evidence['placement']['functions']:
        functions.append({'symbol':row['symbol'],'compiled_bytes':row['compiled_bytes'],
                          'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{
                          'symbol':row['symbol'],'package_offset':row['stock_package_offset'],
                          'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                          'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-app-tick/suspend-registration.elf',output/'registration.elf')
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Experimental same-entry hybrid; finite state comparison with modeled memcpy.',
                      'Existing power storage remains retained; concurrent mutation and timing unqualified.']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
