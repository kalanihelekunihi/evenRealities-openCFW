# SPDX-License-Identifier: MIT
"""Low-power policy with decoded stateful query/switching helpers."""
import json,random,subprocess
from verify_gx8002_clock_switch_1m import verify as qualify, execute as switch_outer, expected as outer_expected
from execute_gx8002_clock_gate_query import execute as gate_query
from verify_gx8002_clock_lowpower_init import execute
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from execute_gx8002_clock_module_query import execute as query
from execute_gx8002_clock_module_source import execute as switch
from oracle_gx8002_clock_module_source import expected as transition
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import sha

def verify():
    evidence=qualify();table,context=load();modules={x['module']:x for x in context['modules']};runners,helper_evidence=load_helpers();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={};hashes={}
    for name,report_name in (('clock-lowpower-init-shared','gx8002-clock-lowpower-init-shared-source-verification.json'),('clock-gate-query-fixed','gx8002-clock-gate-query-fixed-source-verification.json'),('clock-module-query','gx8002-clock-module-query-source-verification.json'),('clock-module-source-fixed','gx8002-clock-module-source-fixed-source-verification.json')):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(p.read_bytes(),name);row=json.loads((ROOT/'docs/research'/report_name).read_text())['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256'];codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    top=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text())
    outer=decode((ROOT/'build/gx8002-board/clock-lowpower-init-shared-candidate.disassembly.txt').read_text());rng=random.Random(556);cases=0
    for i in range(128):
        state={base+off:rng.getrandbits(32) for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)};initial=dict(state);calls=[]
        def get(module):
            value,trace=query(codes['clock-module-query'],0x10024d70,module,table,lambda m:(0,runners['lookup_runner'](m)),state)
            row=modules[module];off=row['clock_offset'];word=state[0xa001008c if module<10 else 0xa0300088];want=(word>>off)&1
            if module in (0,1,6,9) and word&(1<<(off+1)):want=2
            if module==7:want=3+int(want!=0)
            if module==8:want=5+int(want!=0)
            assert value==want;calls.append(('get',module,value));return value
        def set_source(module,source):
            result=switch(codes['clock-module-source-fixed'],0x10024be0,module,source,table,modules,state,**runners);assert result==transition(module,source,modules,state);state.update(result[3]);calls.append(('set',module,source));return result[0]
        # Independent policy replay using only descriptor-based transition model.
        model=dict(initial)
        for module in range(26):
            source=0
            if module in (7,8):
                bit=(model[0xa001008c]>>modules[module]['clock_offset'])&1
                if bit:continue
                source=4 if module==7 else 6
            elif module==2:
                bit=(model[0xa001008c]>>modules[module]['clock_offset'])&1
                if bit and model[0xa001008c]&64:continue
            model=transition(module,source,modules,model)[3]
        expected_answers={}
        for module in range(11,26):
            value=model[0xa0300018];off=modules[module]['gate_all_offset']
            offsets=[modules[module+i]['gate_all_offset'] for i in (1,2)] if module in (16,19,22) else [off]
            expected_answers[module]=0xffffffff if off==0 else int(any(not ((value>>(v&31))&1) for v in offsets))
        low_calls=[]
        def lowpower():
            trace=execute(outer,0x1002599c,{2:0,7:0,8:0},0,get,set_source,lambda:state[0xa001008c])
            assert [x for x in trace if x[0]!='read']==calls
            assert state==model;low_calls.append(True)
        def gate(module):
            value,trace=gate_query(codes['clock-gate-query-fixed'],0x10025180,module,table,lambda m:(0,runners['lookup_runner'](m)),state)
            assert value==expected_answers[module];return value
        saved=rng.getrandbits(32);enable=(0,1,2,0xffffffff)[i%4]
        result=switch_outer(top,0x10025a14,{},saved,enable,(28,0,18,1),gate_runner=gate,lowpower_runner=lowpower)
        assert result==outer_expected(expected_answers,saved,enable) and low_calls==[True]
        assert state==model;cases+=1
    return {'evidence':evidence,'cases':cases,'dependency_elf_sha256':hashes,'helpers':helper_evidence,'source_admitted':False,'limits':['Stateful decoded helper frames marshalled across policy calls; each transition and final state match independent models. Outer low-power call and subsequent decoded gate queries share state. Selector/divider/PLL/copy modeled here; physical clock timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-lowpower.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
