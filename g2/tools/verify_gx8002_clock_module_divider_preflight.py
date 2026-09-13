# SPDX-License-Identifier: MIT
"""Early decoded module divider boundaries; no successful-write admission."""
import json,subprocess
from build_gx8002_clock_module_divider_set_candidate import build
from load_gx8002_clock_context import load,ROOT
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_module_divider_preflight import execute
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
    cases=0
    for module in list(range(32))+[0x7fffffff,0x80000000,0xffffffff]:
        for divider in (0,1,2,255,256,32767,32768,65535):
            dest=modules[module]['divider'] if module in modules else 0
            expected='divider' if dest and table[dest] else 'return'
            a=execute(stock,0x16e0c,module,divider,table,nested)
            b=execute(source,0x10024df8,module,divider,table,nested)
            assert a==b and a[0]==expected,(module,divider,a,b,expected);cases+=1
    return {'candidate':candidate,'cases':cases,'context':context,'source_admitted':False,'limits':['Decoded early returns and nested lookup; verifies current-divider helper parameter/base arguments before stopping. Successful register writes, remaining helper calls and complete function ABI remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-divider-preflight.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
