# SPDX-License-Identifier: MIT
"""Shared clock/lookup/divider with source-built parameter and divider tables."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from verify_gx8002_clock_divider import build
from analyze_gx8002_upstream_objects import IMAGE
from decode_gx8002_stock_clock import stock_code


def verify():
    placement=analyze();leaf=build();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text());code.update(decode((ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text()))
    elf=Elf32((out/'placement.elf').read_bytes(),'actual clock tables')
    sections={s['name']:s for s in elf.sections}
    table=struct.unpack('<19I',elf.contents(sections['.rodata.open_cfw_gx8002_clock_frequency']))
    records=elf.contents(sections['.data.gx_clock_param_table'])
    divs=elf.contents(sections['.data.gx_clock_div_table'])
    stock=IMAGE.read_bytes()
    if records!=stock[0x186f4:0x18894] or divs!=stock[0x18898:0x188dc]:raise ValueError('Actual table identity')
    cells={}
    for i in range(26):
        for off in (8,12):cells[0x200266e0+i*16+off,4]=struct.unpack_from('<I',records,i*16+off)[0]
    for i in range(17):
        addr=0x20026884+i*4;off,shift,mask=struct.unpack_from('<BBH',divs,i*4)
        cells[addr,1]=off;cells[addr+1,1]=shift;cells[addr+2,2]=mask
        for base in (0xa0010000,0xa0300000):cells[base+off,4]=0
    original_code=stock_code();original_switch=struct.unpack_from('<19I',stock,0x17474)
    dto_section=sections['.data.gx_clock_dto_table'];dto_bytes=elf.contents(dto_section)
    for i,off in enumerate(dto_bytes):cells[dto_section['address']+i,1]=off
    ids=[struct.unpack_from('<I',records,i*16)[0] for i in range(26)]
    count=0
    for module,register in product(range(26),(0,1,0x1ffffff,0x8000000,0xffffffff)):
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        index=ids.index(mapped);offset=records[index*16+6]
        base=0xa0010000 if mapped<10 else 0xa0300000
        state=cells.copy()
        for address,width in list(state):
            if address>=0xa0000000:state[address,width]=register
        for off in dto_bytes:
            for bank in (0xa0010000,0xa0300000):state[bank+off,4]=register
        state[0xa001008c,4]=0;state[0xa0300088,4]=0
        if module not in (7,8):state[base+(0x8c if mapped<10 else 0x88),4]=1<<offset
        candidate_reads=[];stock_reads=[]
        result,calls=execute(code,table,module,0,0,lookup_records=records,source_cells=state,mmio_trace=candidate_reads)
        original=execute(original_code,original_switch,module,0,0,lookup_records=records,source_cells=state,mmio_trace=stock_reads)
        if candidate_reads!=stock_reads:raise ValueError('Stock/source MMIO trace mismatch')
        if (result,calls)!=original:raise ValueError('Stock/source high-frequency mismatch')
        hz=24576000;div=0
        if module not in (7,8):
            dto_ptr=struct.unpack_from('<I',records,index*16+12)[0]
            if dto_ptr:
                word=state[base+state[dto_ptr,1],4]
                if not word&(1<<27):hz=((word&0x1ffffff)*hz)>>25
            pointer=struct.unpack_from('<I',records,index*16+8)[0]
            if pointer:
                off,shift,mask=struct.unpack_from('<BBH',divs,pointer-0x20026884)
                field=(state[base+off,4]>>shift)&mask;div=field+1 if field else 0
            if div:hz//=div
        wanted=[] if module in (7,8) else [('lookup',mapped),('divider',div)]
        if (result,calls)!=(0 if module in (7,8) else hz,wanted):raise ValueError('Actual high-frequency oracle')
        count+=1
    return {'placement':placement,'divider':leaf,'decoded_cases':count,'ordered_mmio_compared':True,'source_admitted':False,
            'limits':['Shared candidate and both helper bodies with actual source records; 24 MHz source and real DTO/divider records with varied registers. PLL and hardware pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-stock-high.json').write_text(json.dumps(report,indent=2)+'\n');print('Stock/source high cases:',report['decoded_cases'])
