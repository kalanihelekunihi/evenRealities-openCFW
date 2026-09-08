#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit source-authored flash dispatch data after target layout checks."""
import contextlib,io,json,shutil
from build_gx8002_flash_interface_table import build,ROOT
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    symbol='open_cfw_gx8002_flash_interface'
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/flash-interface-table.elf',output/'flash-interface-table.elf')
    return {'functions':[{'symbol':symbol,'section_name':'.data.flash_interface',
              'ownership_kind':'generated_source_data','compiled_bytes':120,
              'compiled_sha256':evidence['compiled_sha256'],
              'stock_occurrences':[{'symbol':symbol,'package_offset':0x18518,'bytes':120,
                  'sha256':evidence['compiled_sha256'],'region':'image_a_sram_data'}]}],
            'evidence':evidence,'source_admitted':True,'hardware_qualified':False,
            'limits':['Target dispatch layout and source function references recovered. The upstream API has type differences from recovered internal prototypes; whole-source public API integration and hardware qualification remain.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-interface-table-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
