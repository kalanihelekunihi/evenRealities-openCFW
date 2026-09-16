# SPDX-License-Identifier: MIT
"""Compare complete backup divider programming with descriptor-based oracle."""
import json,struct,subprocess
from itertools import product
from build_gx8002_backup_clock_rate_setters import build,ROOT,Elf32
from build_gx8002_backup_clock_tables import build as tables_build
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA,sha
from execute_gx8002_clock_module_divider import execute
from oracle_gx8002_clock_module_divider import expected
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
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3c0c8','--stop-address=0x3c228',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-clock-rate-setters/divider.disassembly.txt').read_text());cases=0
    def lookup(module):
        if module not in modules:return 0xffffffff,()
        base=0xa0010000 if module<10 else 0xa0300000
        return 0,(modules[module]['address'],base,base+(0x8c if module<10 else 0x88),base+0x18,base+0x1c,base+0x20)
    def check(module,divider,registers):
        args=(module,divider,table,lookup,registers)
        a=execute(old,0x3c0c8,*args,stock_delta=0x10003000-0x3b940,lookup_address=0x100034e0)
        b=execute(new,0x10003788,*args,lookup_address=0x100034e0)
        want=expected(module,divider,table,modules,registers)
        clean=lambda result:([x for x in result[0] if x[0] not in ('set','divider')],result[1])
        assert clean(a)==clean(b),(module,divider,a,b)
        assert clean(b)==clean(want),(module,divider,'oracle mismatch')
    for module,divider,initial in product((*range(32),0x7fffffff,0x80000000,0xffffffff),(0,1,2,255,256,32767,32768,65535),(0,0xffffffff,0xaaaaaaaa,0x55555555)):
        registers={b+o:initial for b in (0xa0010000,0xa0300000) for o in (0x18,0x1c,0x20,0x88,0x8c)}
        for row in modules.values():
            ptr=row['divider']
            if ptr:registers[(0xa0010000 if row['module']<10 else 0xa0300000)+table[ptr]]=initial
        check(module,divider,registers)
        cases+=1
    targeted=0
    for module,row in modules.items():
        ptr=row['divider']
        if not ptr or not table[ptr]:continue
        base=0xa0010000 if module<10 else 0xa0300000
        address=base+table[ptr];shift=table[ptr+1];mask=table[ptr+2]|table[ptr+3]<<8
        for field in sorted({0,1,mask//2,mask}):
            current=field+1 if field else 0
            for divider,fast,inhibited in product(sorted({0,1,2,current,mask,mask+1,65535}),(0,1),(0,1)):
                registers={base+off:0xa5a5a5a5 for off in (0x18,0x1c,0x20,0x88,0x8c)}
                registers[address]=(0xa5a5a5a5&~(mask<<shift))|(field<<shift)
                clock=row['clock_offset'];high=row['gate_high_offset']
                source_address=base+(0x8c if module<10 else 0x88)
                registers[source_address]=(registers[source_address]&~(1<<clock))|(fast<<clock)
                if high>=0:registers[base+0x18]=(registers[base+0x18]&~(1<<high))|(inhibited<<high)
                check(module,divider,registers);targeted+=1;cases+=1
    report={'cases':cases,'targeted_cases':targeted,'candidate':evidence,'limits':['Complete decoded stock/source divider with authenticated immutable descriptors and modeled lookup. Inlined getters/register updates execute; independent ordered MMIO oracle. Physical timing and mutable tables unqualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-divider-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'divider cases passed')
