#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Structural DW SPI cleanup proof with stock identity."""
import json
import shutil
from build_gx8002_dw_spi_cleanup_candidate import ROOT, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
ADDRESS=0x10206164


def prove(code):
    sequence=[('ld.w','r3, (r0, 0x0)',2),('movi','r2, 0',2),
              ('ld.w','r3, (r3, 0x18)',2),('ld.w','r3, (r3, 0x4)',2),
              ('st.w','r2, (r3, 0x8)',2),('rts','',2)]
    pc=ADDRESS
    for instruction in sequence:
        if code.get(pc)!=instruction:raise ValueError('DW SPI cleanup instruction contract')
        pc+=instruction[2]
    if pc!=ADDRESS+12:raise ValueError('DW SPI cleanup boundary')
    return {'pointer_read_offsets':[0,24,4],'final_store_offset':8,'stored_value':0,'stack_bytes':0,'return':'void','callee_saved':'unchanged'}


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build()
    semantics=prove(decode((ROOT/'build/gx8002-board/dw-spi-cleanup-candidate.disassembly.txt').read_text()))
    if evidence['compiled_bytes']!=12 or evidence['compiled_sha256']!=evidence['stock_sha256']:
        raise ValueError('DW SPI cleanup stock equality')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':0xf6f0,'bytes':12,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/dw-spi-cleanup-candidate.elf',output/'dw-spi-cleanup.elf')
    return {'functions':[row],'evidence':evidence,'semantics':semantics,'source_admitted':True,'hardware_qualified':False,
            'limits':['Three ordered pointer loads and one zero store, byte-identical stock, leaf ABI. Requires a valid initialized pointer chain; no hardware interpretation or null-pointer guarantee.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-dw-spi-cleanup-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
