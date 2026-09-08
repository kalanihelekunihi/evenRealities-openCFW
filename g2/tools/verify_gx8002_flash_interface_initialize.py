#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admission adapter for the full decoded flash-interface initializer."""
import contextlib,io,json,shutil
from compare_gx8002_flash_interface_full import verify as compare
from verify_gx8002_logging import check_paths
from link_gx8002_uart_console import ROOT

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):comparison=compare()
    row=comparison['selection']['build']
    if not row['fits']:raise ValueError('interface initializer exceeds envelope')
    if comparison['stock_frame_bytes']!=comparison['candidate_frame_bytes']:raise ValueError('interface frame changed')
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/flash-interface.elf',output/'flash-interface.elf')
    return {'functions':[{'symbol':'open_cfw_gx8002_flash_interface_initialize','section_name':'.text',
        'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
        'stock_occurrences':[{'symbol':'flash_interface_initialize','package_offset':row['package_offset'],
        'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'image_a_sram_text'}]}],
        'evidence':comparison,'source_admitted':True,'hardware_qualified':False,
        'limits':['Decoded full routine with modeled services; interface/BSS ownership and physical startup remain unqualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-interface-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
