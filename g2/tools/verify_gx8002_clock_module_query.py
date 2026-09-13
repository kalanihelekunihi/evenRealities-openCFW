# SPDX-License-Identifier: MIT
"""Stock/source clock queries against decoded lookup and an independent bit model."""
import json,random,subprocess
from build_gx8002_clock_module_query_candidate import build
from load_gx8002_clock_context import load,ROOT
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_module_query import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA

def verify():
    candidate=build();table,context=load();modules={x['module']:x for x in context['modules']};ids=[x['module'] for x in context['modules']]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x16d84','--stop-address=0x16e0c',str(p)],text=True))
    p=ROOT/'build/gx8002-board/clock-module-query-candidate.elf';source=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    helper=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-platform-gate/tables.elf')],text=True))
    def nested(module):
        status,values,writes=lookup(helper,0x10024a44,module,0x1000,ids)
        assert all(0x1000<=a<0x1018 for a,v in writes)
        return status,values
    rng=random.Random(8961);cases=0
    for module in list(range(32))+[0x7fffffff,0x80000000,0xffffffff]:
        for value in [0,0xffffffff,0xaaaaaaaa,0x55555555]+[1<<i for i in range(32)]+[rng.getrandbits(32) for _ in range(128)]:
            registers={0xa001008c:value,0xa0300088:value};expected=0xffffffff;trace=[('lookup',module,0 if module in modules else 0xffffffff)]
            if module in modules:
                offset=modules[module]['clock_offset']
                if offset!=-1:
                    trace.append(('read',0xa001008c if module<10 else 0xa0300088,value))
                    expected=2 if module in (0,1,6,9) and value&(1<<(offset+1)) else (value>>offset)&1
                    if module==7:expected=3+int(expected!=0)
                    if module==8:expected=5+int(expected!=0)
            a=execute(stock,0x16d84,module,table,nested,registers)
            b=execute(source,0x10024d70,module,table,nested,registers)
            assert a==b==(expected,trace),(module,value,a,b,expected,trace)
            cases+=1
    return {'candidate':candidate,'cases':cases,'context':context,'limits':['Decoded stock/source query and nested lookup; independent bit selection model, integer ABI and table immutability checked. Lookup private output marshalled to caller frame. Physical MMIO timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-query.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
