# SPDX-License-Identifier: MIT
"""Stock/upstream equivalence and corrected grouped gate query qualification."""
import json,subprocess,random
from build_gx8002_clock_gate_query_candidate import build as baseline
from build_gx8002_clock_gate_query_fixed_candidate import build as fixed
from load_gx8002_clock_context import load,ROOT
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_gate_query import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA


def verify():
    original=baseline();candidate=fixed();table,context=load();rows=context['modules'];by_id={r['module']:r for r in rows};ids=[r['module'] for r in rows]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');stock=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(stock.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17194','--stop-address=0x17200',str(stock)],text=True))
    base=decode((ROOT/'build/gx8002-board/clock-gate-query-candidate.disassembly.txt').read_text());new=decode((ROOT/'build/gx8002-board/clock-gate-query-fixed-candidate.disassembly.txt').read_text());helper=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-platform-gate/tables.elf')],text=True))
    def nested(module):
        status,values,writes=lookup(helper,0x10024a44,module,0x1000,ids);assert all(0x1000<=a<0x1018 for a,v in writes);return status,values
    rng=random.Random(954);values=[0,0xffffffff,0xaaaaaaaa,0x55555555]+[1<<i for i in range(32)]+[(1<<i)^0xffffffff for i in range(32)]+[rng.getrandbits(32) for _ in range(64)]
    cases=0;differences=0
    for module in list(range(32))+[0x7fffffff,0x80000000,0xffffffff]:
        for value in values:
            registers={0xa0010018:value,0xa0300018:value}
            a=execute(old,0x17194,module,table,nested,registers);b=execute(base,0x10025180,module,table,nested,registers);c=execute(new,0x10025180,module,table,nested,registers)
            assert a==b,(module,value,a,b)
            status,unused=nested(module);trace=[('lookup',module,status)]
            if module not in by_id or by_id[module]['gate_all_offset']==0:want=0xffffffff
            else:
                row=by_id[module];trace.append(('read',0xa0010018 if module<10 else 0xa0300018,value))
                if module in (16,19,22):
                    # Resolve children by their module IDs, independently of table row arithmetic.
                    offsets=[by_id[module+i]['gate_all_offset'] for i in (1,2)]
                    want=int(any(not (value>>off)&1 for off in offsets))
                else:want=int(not (value>>(row['gate_all_offset']&31))&1)
            assert c==(want,trace),(module,value,c,want,trace)
            if a!=c:assert module in (16,19);differences+=1
            cases+=1
    return {'baseline':original,'candidate':candidate,'cases':cases,'corrected_stock_differences':differences,'context':context,'source_admitted':False,'limits':['Decoded stock/upstream equality and corrected result/MMIO trace oracle with decoded authenticated table lookup. Private lookup output frame marshalled. Physical clock behavior remains unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-gate-query.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['corrected_stock_differences'])
