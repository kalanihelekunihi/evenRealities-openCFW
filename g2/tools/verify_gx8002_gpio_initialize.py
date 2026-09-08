#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Structural GPIO initialization call/write/ABI proof with stock identity."""
import json
import shutil
from build_gx8002_gpio_initialize_candidate import ROOT, build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
ADDRESS=0x102060d0


def prove(code):
    sequence=[('push','r15',2),('movi','r1, 1',2),('movi','r0, 4',2),
              ('bsr','0x10025080',4),('movi','r3, 32773',4),
              ('rotli','r3, r3, 29',4),('movi','r0, 0',2),
              ('st.w','r0, (r3, 0x34)',2),('pop','r15',2)]
    pc=ADDRESS
    for instruction in sequence:
        if code.get(pc)!=instruction:raise ValueError('GPIO initialize instruction contract')
        pc+=instruction[2]
    if pc!=ADDRESS+24:raise ValueError('GPIO initialize boundary')
    return {'ordered_effects':[['platform_gate',4,1],['write32',0xa0001034,0]],
            'return':0,'stack_bytes':4,'callee_saved':'unchanged; return address saved across gate call'}


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build()
    semantics=prove(decode((ROOT/'build/gx8002-board/gpio-initialize-candidate.disassembly.txt').read_text()))
    if evidence['compiled_bytes']!=24 or evidence['compiled_sha256']!=evidence['stock_sha256']:
        raise ValueError('GPIO initialize stock equality')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':0xf65c,'bytes':24,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/gpio-initialize-candidate.elf',output/'gpio-initialize.elf')
    return {'functions':[row],'evidence':evidence,'semantics':semantics,'source_admitted':True,'hardware_qualified':False,
            'limits':['Exact straight-line instruction contract and byte-identical stock. Gate helper must preserve ABI; its internal MMIO is separately qualified. No GPIO electrical proof.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-gpio-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
