# SPDX-License-Identifier: MIT
"""Decoded DTO programming traces; no source admission."""
import json,subprocess
from oracle_gx8002_clock_module_dto import expected
from load_gx8002_clock_decoded_helpers import load_helpers
from build_gx8002_clock_module_dto_set_candidate import build
from load_gx8002_clock_context import load,ROOT
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_module_dto import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha

def verify():
    candidate=build();table,context=load();modules={x['module']:x for x in context['modules']};ids=[x['module'] for x in context['modules']]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x16f58','--stop-address=0x17020',str(p)],text=True))
    source=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/clock-module-dto-set-candidate.elf')],text=True))
    helper=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-platform-gate/tables.elf')],text=True))
    def nested(module):
        status,values,writes=lookup(helper,0x10024a44,module,0x1000,ids);assert all(0x1000<=a<0x1018 for a,v in writes);return status,values
    runners,leaf_evidence=load_helpers()
    def run(*args):return execute(*args,register_runner=runners['register_runner'])
    cases=0
    for module in list(range(32))+[0x7fffffff,0x80000000,0xffffffff]:
        for dto in (0,1,0x1ffffff,0xffffffff):
            for enable in (0,1,2,0xffffffff):
                for value in (0,0xffffffff,0xaaaaaaaa,0x55555555):
                    registers={}
                    for base in (0xa0010000,0xa0300000):
                        for off in (0x18,0x1c,0x20,0x88,0x8c):registers[base+off]=value
                    for row in modules.values():
                        ptr=row['dto']
                        if ptr:registers[(0xa0010000 if row['module']<10 else 0xa0300000)+table[ptr]]=value
                    a=run(stock,0x16f58,module,dto,enable,table,nested,registers)
                    b=run(source,0x10024f44,module,dto,enable,table,nested,registers)
                    want=expected(module,dto,enable,table,modules,registers)
                    assert a==b==want,(module,dto,enable,value,a,b,want);cases+=1
    targeted=0
    for module,row in modules.items():
        ptr=row['dto']
        if not ptr or not table[ptr]:continue
        base=0xa0010000 if module<10 else 0xa0300000;address=base+table[ptr];source_addr=base+(0x8c if module<10 else 0x88)
        for current in (0,1,0x1ffffff):
            for dto in (0,1,0x1ffffff,0xffffffff):
                for enabled in (0,1):
                    for enable in (0,1,2,0xffffffff):
                        for fast in (0,1):
                            for inhibited in (0,1):
                                registers={base+off:0 for off in (0x18,0x1c,0x20,0x88,0x8c)}
                                registers[address]=current|(int(not enabled)<<27)
                                registers[source_addr]=fast<<row['clock_offset']
                                if row['gate_high_offset']>=0:registers[base+0x18]=inhibited<<row['gate_high_offset']
                                a=run(stock,0x16f58,module,dto,enable,table,nested,registers)
                                b=run(source,0x10024f44,module,dto,enable,table,nested,registers)
                                want=expected(module,dto,enable,table,modules,registers)
                                assert a==b==want,(module,current,dto,enabled,enable,fast,inhibited,a,b,want)
                                cases+=1;targeted+=1
    return {'candidate':candidate,'cases':cases,'targeted_cases':targeted,'context':context,'decoded_helper_evidence':leaf_evidence,'source_admitted':False,'limits':['Decoded full stock/source comparison and independent pulse/temporary switching oracle. Lookup and register update helpers decoded with private frame/MMIO snapshot marshalling. Physical timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-dto-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
