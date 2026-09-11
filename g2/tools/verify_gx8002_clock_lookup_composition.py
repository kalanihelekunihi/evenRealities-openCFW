# SPDX-License-Identifier: MIT
"""Decoded lookup-to-frequency-gate composition with authenticated table records."""
import json
import struct
import subprocess
from itertools import product
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32
from compare_gx8002_clock_lookup import execute as lookup
from verify_gx8002_clock_lookup_result import execute as gate
from verify_gx8002_frequency_dispatch import expected as dispatch
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE


def verify():
    placement=analyze();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16a58','--stop-address=0x173c0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    out=ROOT/'build/gx8002-clock-frequency-table-probe'
    new=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'lookup composition')
    sec=next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table')
    records=elf.contents(sec)
    if records!=IMAGE.read_bytes()[0x186f4:0x18894]:raise ValueError('Lookup records differ from stock')
    ids=[struct.unpack_from('<I',records,i*16)[0] for i in range(26)]
    count=0;observed_offsets=set()
    for use_lookup,use_gate,module in product((False,True),(False,True),(*range(256),0x7fffffff,0x80000000,0xffffffff)):
        kind,mapped=dispatch(module)
        if kind=='return':continue
        result,info,writes=lookup(new if use_lookup else old,0x10024a44 if use_lookup else 0x16a58,mapped,0x1000,ids)
        if result==0:
            index=(info[0]-sec['address'])//16
            if not 0<=index<26 or info[0]!=sec['address']+16*index:raise ValueError('Lookup descriptor address')
            byte=records[index*16+6];observed_offsets.add(byte)
        else:byte=0
        trace,kind,value=gate(new if use_gate else old,use_gate,result,byte)
        if result or byte==255:
            if (kind,value)!=('return',0):raise ValueError('Composed lookup rejection')
        elif kind!='selection' or value!=byte:
            raise ValueError('Composed lookup offset')
        count+=1
    return {'placement':placement,'decoded_cases':count,'observed_offset_bytes':sorted(observed_offsets),'source_admitted':False,
            'limits':['Dispatch mapping modeled; decoded lookup output translated into fixed gate entry state. Separate frames, no full-function ABI or concurrent table mutation proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-lookup-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['decoded_cases'],report['observed_offset_bytes'])
