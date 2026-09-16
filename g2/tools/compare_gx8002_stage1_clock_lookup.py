# SPDX-License-Identifier: MIT
"""Verify source-built stage-one clock lookup with independent search oracle."""
import json,struct,subprocess
from build_gx8002_stage1_clock_tables import build as tables,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from compare_gx8002_backup_clock_lookup import execute as run


def execute(code,start,module,pointer,ids):
    return run(code,start,module,pointer,ids,record_base=0x200014c8)


def verify():
    evidence=tables();output=ROOT/'build/gx8002-stage1-clock-tables';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    elf=Elf32(wrapper.read_bytes(),str(wrapper));assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x38a8c','--stop-address=0x38b4c',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text',str(output/'tables.elf')],text=True))
    offset=0x200014c8-0x20000000+0x38954
    original=[struct.unpack_from('<I',stock,offset+i*16)[0] for i in range(26)];cases=0
    variants=[original,list(range(26)),list(reversed(range(26))),[0xffffffff]*26]
    variants += [[m if i in (j,25) else 0xffffffff for i in range(26)] for m in range(26) for j in range(26)]
    for ids in variants:
        for module in [*range(28),0x7fffffff,0x80000000,0xffffffff]:
            for pointer in (0,0x1000):
                expected=[0xa5a5a5a5]*6;writes=[];result=0xffffffff
                if pointer and module<26:
                    expected[0]=0;writes=[(pointer,0)]
                    index=module if ids[module]==module else next((i for i,v in enumerate(ids) if v==module),None)
                    if index is not None:
                        base=0xa0010000 if module<10 else 0xa0300000
                        expected=[0x200014c8+index*16,base,base+(0x8c if module<10 else 0x88),base+24,base+28,base+32]
                        writes += [(pointer+i*4,v) for i,v in enumerate(expected)];result=0
                oracle=(result,expected,writes)
                if execute(old,0x38a8c,module,pointer,ids)!=oracle or execute(new,0x10000138,module,pointer,ids)!=oracle:raise ValueError('clock lookup mismatch')
                cases+=1
    report={'evidence':evidence,'cases':cases,'source_admitted':False,'limits':['Finite decoded execution; ordinary RAM reads may be optimized.', 'No concurrent table mutation, overlapping output, hardware or timing qualification.']}
    (ROOT/'docs/research/gx8002-stage1-clock-lookup-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
