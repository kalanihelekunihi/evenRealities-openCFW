#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Structural SPI list-head initialization proof with stock identity."""
import json
import shutil
from build_gx8002_device_list_init_candidate import ROOT, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
ADDRESS=0x102060e8


def prove(code):
    sequence=[('lrw','r3, 0x20027ad0',2),('addi','r2, r3, 8',2),
              ('st.w','r3, (r3, 0x0)',2),('st.w','r3, (r3, 0x4)',2),
              ('st.w','r2, (r3, 0x8)',2),('st.w','r2, (r3, 0xc)',2),('rts','',2)]
    pc=ADDRESS
    for instruction in sequence:
        if code.get(pc)!=instruction:raise ValueError('GPIO initialize instruction contract')
        pc+=instruction[2]
    if pc!=ADDRESS+14:raise ValueError('GPIO initialize boundary')
    return {'ordered_writes': [[0x20027ad0,0x20027ad0],[0x20027ad4,0x20027ad0],[0x20027ad8,0x20027ad8],[0x20027adc,0x20027ad8]],'stack_bytes':0,'return':'void','callee_saved':'unchanged'}


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build()
    semantics=prove(decode((ROOT/'build/gx8002-board/device-list-init-candidate.disassembly.txt').read_text()))
    if evidence['compiled_bytes']!=20 or evidence['compiled_sha256']!=evidence['stock_sha256']:
        raise ValueError('GPIO initialize stock equality')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':0xf674,'bytes':20,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/device-list-init-candidate.elf',output/'device-list-init.elf')
    return {'functions':[row],'evidence':evidence,'semantics':semantics,'source_admitted':True,'hardware_qualified':False,
            'limits':['Four ordered pointer stores and leaf ABI, byte-identical stock. Registry operations and concurrency remain separate.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-device-list-init-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
