#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapters for qualified application startup and reboot."""
import contextlib
import io
import json
import shutil
from compare_gx8002_app_initialize import verify as compare_startup
from compare_gx8002_reboot import verify as compare_reboot
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT


def verify(kind,prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=(compare_startup if kind=='startup' else compare_reboot)()
    functions=[]
    rows=evidence['placement']['sections' if kind=='startup' else 'functions']
    for row in rows:
        section=row.get('section','.text.'+row.get('symbol',''))
        data=section.startswith('.rodata.')
        symbol=section[8:] if data else section[6:]
        functions.append({'symbol':symbol,'section_name':section,
                          'ownership_kind':'generated_source_data' if data else 'compiled_c',
                          'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
                          'stock_occurrences':[{'symbol':symbol,'package_offset':row['package_offset'],
                          'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],
                          'region':'image_a_xip_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-app-tick'/('app-initialize.elf' if kind=='startup' else 'reboot.elf'),output/(kind+'.elf'))
    return {'functions':functions,'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Service calls modeled; state and hardware timing remain unqualified.',
                      'Reboot wait is verified stock behavior, not replacement for missing functionality.']}


def startup(prefix=None,sdk=None,output=None):return verify('startup',prefix,sdk,output)
def reboot(prefix=None,sdk=None,output=None):return verify('reboot',prefix,sdk,output)

if __name__=='__main__':
    for kind in ('startup','reboot'):
        (ROOT/f'docs/research/gx8002-{kind}-verification.json').write_text(json.dumps(verify(kind),indent=2)+'\n')
