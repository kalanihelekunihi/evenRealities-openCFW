#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapters for the qualified native macOS logging candidates."""
import contextlib
import io
import json
import shutil
from compare_gx8002_format import verify as compare_format
from compare_gx8002_printf_abi import verify as compare_printf
from analyze_gx8002_upstream_objects import IMAGE, sha
from link_gx8002_uart_console import ROOT


def check_paths(prefix, sdk):
    # Underlying upstream probes currently use these explicit native inputs.
    if prefix and prefix.resolve() != (ROOT/'build/csky-macos/install/bin').resolve():
        raise ValueError('logging qualification requires native macOS compiler path')
    if sdk and sdk.resolve() != (ROOT/'build/upstream-nationalchip-lvp-kws').resolve():
        raise ValueError('logging qualification requires pinned SDK path')


def formatter(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()): evidence=compare_format()
    placement=evidence['helper_evidence']['integer_evidence']['placement']
    rows=[]
    for row in placement['functions']:
        if row['symbol']=='putf' and not row['byte_exact']:raise ValueError('output helper lost exact match')
        rows.append({'symbol':row['symbol'],'compiled_bytes':row['compiled_bytes'],
                     'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{
                     'symbol':row['symbol'],'package_offset':row['package_offset'],
                     'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                     'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-tinyprintf/formatter.elf',output/'formatter.elf')
    return {'functions':rows,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'license_notice_sha256':sha((ROOT/'components/shared/gx8002/TINYPRINTF-NOTICE.txt').read_bytes()),
            'limits':['Experimental same-entry hybrid; finite target comparison with modeled helper calls.',
                      'Malformed widths, undefined input behavior and hardware timing remain unqualified.']}


def printf(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=compare_printf()
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-printf/printf.elf',output/'printf.elf')
    symbol='open_cfw_gx8002_printf'
    return {'symbol':symbol,'compiled_bytes':evidence['compiled_bytes'],
            'compiled_sha256':evidence['compiled_sha256'],'evidence':evidence,
            'stock_occurrences':[{'symbol':symbol,'package_offset':0x101b0,'bytes':30,
            'sha256':sha(IMAGE.read_bytes()[0x101b0:0x101ce]),'region':'image_a_xip_text'}],
            'source_admitted':True,'hardware_qualified':False,
            'limits':['32-bit argument slots; experimental hybrid only.']}


if __name__=='__main__':
    for name,verify in [('formatter',formatter),('printf',printf)]:
        (ROOT/f'docs/research/gx8002-{name}-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
