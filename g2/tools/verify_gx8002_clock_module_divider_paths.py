# SPDX-License-Identifier: MIT
"""Complete decoded stock/source divider transitions with decoded leaf helpers."""
import json,subprocess,random
from oracle_gx8002_clock_module_divider import expected
from build_gx8002_clock_module_divider_set_candidate import build
from load_gx8002_clock_context import load,ROOT
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_module_divider import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha

def verify():
    candidate=build();table,context=load();modules={x['module']:x for x in context['modules']};ids=[x['module'] for x in context['modules']]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x16e0c','--stop-address=0x16f58',str(p)],text=True))
    source=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/clock-module-divider-set-candidate.elf')],text=True))
    helper=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-platform-gate/tables.elf')],text=True))
    def nested(module):
        status,values,writes=lookup(helper,0x10024a44,module,0x1000,ids);assert all(0x1000<=a<0x1018 for a,v in writes);return status,values
    from load_gx8002_divider_decoded_helpers import load as load_leaves
    runners,leaf_evidence=load_leaves()
    def run(*args):return execute(*args,**runners)
    cases=0;rng=random.Random(7896);changed=0
    for module in list(range(32))+[0x7fffffff,0x80000000,0xffffffff]:
        for divider in (0,1,2,255,256,32767,32768,65535):
            for value in (0,0xffffffff,0xaaaaaaaa,0x55555555,rng.getrandbits(32)):
                registers={}
                for base in (0xa0010000,0xa0300000):
                    for off in (0x18,0x1c,0x20,0x88,0x8c):registers[base+off]=value
                for row in modules.values():
                    ptr=row['divider']
                    if ptr:registers[(0xa0010000 if row['module']<10 else 0xa0300000)+table[ptr]]=value
                a=run(stock,0x16e0c,module,divider,table,nested,registers)
                b=run(source,0x10024df8,module,divider,table,nested,registers)
                want=expected(module,divider,table,modules,registers)
                assert a==b==want,(module,divider,value,a,b,want)
                changed+=int(any(t[0]=='write' for t in a[0]));cases+=1
    targeted=0
    for module,row in modules.items():
        ptr=row['divider']
        if not ptr or not table[ptr]:continue
        base=0xa0010000 if module<10 else 0xa0300000;address=base+table[ptr];shift=table[ptr+1];mask=table[ptr+2]|table[ptr+3]<<8
        high=row['gate_high_offset'];clock=row['clock_offset'];assert 0<=clock<32
        for field in sorted({0,1,mask//2,mask}):
            current=field+1 if field else 0
            for divider in sorted({0,1,2,current,mask,mask+1,65535}):
                for fast in (0,1):
                    for inhibited in (0,1):
                        registers={base+off:rng.getrandbits(32) for off in (0x18,0x1c,0x20,0x88,0x8c)}
                        registers[address]=(rng.getrandbits(32)&~(mask<<shift))|(field<<shift)
                        source_addr=base+(0x8c if module<10 else 0x88)
                        registers[source_addr]=(registers[source_addr]&~(1<<clock))|(fast<<clock)
                        if high>=0:registers[base+0x18]=(registers[base+0x18]&~(1<<high))|(inhibited<<high)
                        a=run(stock,0x16e0c,module,divider,table,nested,registers)
                        b=run(source,0x10024df8,module,divider,table,nested,registers)
                        want=expected(module,divider,table,modules,registers)
                        assert a==b==want,(module,divider,field,fast,inhibited,a,b,want)
                        changed+=int(any(t[0]=='write' for t in a[0]));cases+=1;targeted+=1
    return {'candidate':candidate,'cases':cases,'targeted_cases':targeted,'writing_cases':changed,'context':context,'decoded_leaves':leaf_evidence,'source_admitted':False,'limits':['Complete stock/source decoded traces, private stores, table immutability and integer ABI. Lookup, current-divider and register-update helpers decoded with private frame/snapshot marshalling. Independent descriptor-based pulse/temporary switching oracle checked. Physical timing remains outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-divider-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
