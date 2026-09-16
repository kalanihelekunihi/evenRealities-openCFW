# SPDX-License-Identifier: MIT
"""Compare backup module switching with immutable authenticated clock tables."""
import json,struct,subprocess
from itertools import product
from build_gx8002_backup_clock_module_source import build,ROOT,Elf32
from build_gx8002_backup_clock_tables import build as tables_build
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA,sha
from execute_gx8002_clock_module_source import execute
from oracle_gx8002_clock_module_source import expected
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();tables_build();elf=Elf32((ROOT/'build/gx8002-backup-clock-tables/tables.elf').read_bytes(),'tables');table={};modules={}
    for sec in elf.sections:
        if sec['flags']&2 and sec['name'].startswith('.data'):table.update(dict(enumerate(elf.contents(sec),sec['address'])))
    param=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    for i in range(26):
        module,high,gate,clock,div,dto=struct.unpack_from('<IbbbxII',param,i*16)
        modules[module]={'module':module,'table_index':i,'address':0x2001699c+i*16,'gate_high_offset':high,'gate_all_offset':gate,'clock_offset':clock,'divider':div,'dto':dto}
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3bf00','--stop-address=0x3c0c8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-clock-module-source/source.disassembly.txt').read_text());cases=0;differences=[]
    scenarios=[(m,s,i,None) for m,s,i in product(range(26),range(10),(0,0xffffffff,0xaaaaaaaa,0x55555555))]
    scenarios += [(m,s,i,None) for m,s,i in product((26,27,0x7fffffff,0x80000000,0xffffffff),(0,1,2,9,0xffffffff),(0,0xffffffff))]
    scenarios += [(m,s,0,(g,c)) for m,s,g,c in product((7,8),range(10),range(8),range(16))]
    for module,source,initial,audio in scenarios:
        mmio={b+o:initial for b in (0xa0010000,0xa0300000) for o in (0x18,0x1c,0x20,0x88,0x8c)}
        if audio is not None:
            gate_bits,clock_bits=audio
            mmio[0xa0010018]=sum(((gate_bits>>i)&1)<<bit for i,bit in enumerate((5,6,19)))
            mmio[0xa001008c]=sum(((clock_bits>>i)&1)<<bit for i,bit in enumerate((6,19,20,21)))
        args=(module,source,table,modules,mmio)
        a=execute(old,0x3bf00,*args,stock_delta=0x10003000-0x3b940,lookup_address=0x100034e0)
        b=execute(new,0x100035c0,*args,lookup_address=0x100034e0)
        wanted=expected(module,source,modules,mmio)
        # Inline register setters have no helper-call events.
        clean=lambda x:(x[0],[c for c in x[1] if c[0]=='lookup'],x[2],x[3])
        assert clean(b)==clean(wanted),(module,source,initial,b,wanted)
        if clean(a)!=clean(b):differences.append({'module':module,'source':source,'initial':initial,'audio':audio})
        cases+=1
    report={'cases':cases,'candidate':evidence,'stock_differences':differences,'limits':['Immutable backup source tables; lookup output modeled. Complete decoded switching with independent ID-based transition oracle. Stock differences recorded explicitly, not equivalence claims. Hardware/timing and mutable tables unqualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-module-source-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    r=verify();print(r['cases'],len(r['stock_differences']))
