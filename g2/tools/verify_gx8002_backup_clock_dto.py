# SPDX-License-Identifier: MIT
"""Compare complete backup dto programming with descriptor-based oracle."""
import json,struct,subprocess
from itertools import product
from build_gx8002_backup_clock_rate_setters import build,ROOT,Elf32
from build_gx8002_backup_clock_tables import build as tables_build
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA,sha
from execute_gx8002_clock_module_dto import execute
from oracle_gx8002_clock_module_dto import expected
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
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3c228','--stop-address=0x3c334',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-clock-rate-setters/dto.disassembly.txt').read_text());cases=0
    def lookup(module):
        if module not in modules:return 0xffffffff,()
        base=0xa0010000 if module<10 else 0xa0300000
        return 0,(modules[module]['address'],base,base+(0x8c if module<10 else 0x88),base+0x18,base+0x1c,base+0x20)
    def check(module,dto,enable,registers):
        args=(module,dto,enable,table,lookup,registers)
        a=execute(old,0x3c228,*args,stock_delta=0x10003000-0x3b940,lookup_address=0x100034e0)
        b=execute(new,0x100038e8,*args,lookup_address=0x100034e0)
        want=expected(module,dto,enable,table,modules,registers)
        clean=lambda result:([x for x in result[0] if x[0] not in ('set','dto')],result[1])
        assert clean(a)==clean(b),(module,dto,a,b)
        assert clean(b)==clean(want),(module,dto,'oracle mismatch')
    for module,dto,enable,initial in product((*range(32),0x7fffffff,0x80000000,0xffffffff),(0,1,0x1ffffff,0xffffffff),(0,1,2,0xffffffff),(0,0xffffffff,0xaaaaaaaa,0x55555555)):
        registers={b+o:initial for b in (0xa0010000,0xa0300000) for o in (0x18,0x1c,0x20,0x88,0x8c)}
        for row in modules.values():
            ptr=row['dto']
            if ptr:registers[(0xa0010000 if row['module']<10 else 0xa0300000)+table[ptr]]=initial
        check(module,dto,enable,registers);cases+=1
    targeted=0
    for module,row in modules.items():
        ptr=row['dto']
        if not ptr or not table[ptr]:continue
        base=0xa0010000 if module<10 else 0xa0300000;address=base+table[ptr];source_address=base+(0x8c if module<10 else 0x88)
        for current,dto,enabled,enable,fast,inhibited in product((0,1,0x1ffffff),(0,1,0x1ffffff,0xffffffff),(0,1),(0,1,2,0xffffffff),(0,1),(0,1)):
            registers={base+off:0 for off in (0x18,0x1c,0x20,0x88,0x8c)}
            registers[address]=current|(int(not enabled)<<27)
            registers[source_address]=fast<<row['clock_offset']
            if row['gate_high_offset']>=0:registers[base+0x18]=inhibited<<row['gate_high_offset']
            check(module,dto,enable,registers);cases+=1;targeted+=1
    report={'cases':cases,'targeted_cases':targeted,'candidate':evidence,'limits':['Complete decoded backup stock/source DTO and independent ordered MMIO oracle. Authenticated immutable tables; lookup modeled, register-update instructions execute inline. Physical timing and mutable state unqualified.']}
    (ROOT/'docs/research/gx8002-backup-clock-dto-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'DTO cases passed')
