# SPDX-License-Identifier: MIT
"""Full init divider/DTO choices through decoded programming and leaf helpers."""
import json,subprocess,random
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_clock_module_divider import execute as divide
from execute_gx8002_clock_module_dto import execute as dto
from oracle_gx8002_clock_module_divider import expected as divider_model
from oracle_gx8002_clock_module_dto import expected as dto_model
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from load_gx8002_divider_decoded_helpers import load as load_leaves
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word


def verify(include_other_state=False,gate_state_runner=None,gate_state_model=None,pll_state_runner=None,pll_state_model=None,copy_runner=None,mode_runner=None,trim_state_runner=None):
    table,context=load();modules={r['module']:r for r in context['modules']};helpers,helper_evidence=load_helpers();leaves,leaf_evidence=load_leaves();codes={};hashes={};pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('clock-module-divider-set','clock-module-dto-set'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);r=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text());row=r['functions'][0];s=next(s for s in e.sections if s['name']==row['section_name']);assert sha(e.contents(s))==row['compiled_sha256'];codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    counts=[0,0]
    addresses={base+off for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)}
    for module,row in modules.items():
        for kind in ('divider','dto'):
            ptr=row[kind]
            if ptr and table[ptr]:addresses.add((0xa0010000 if module<10 else 0xa0300000)+table[ptr])
    def lookup(module):return 0,helpers['lookup_runner'](module)
    def apply(result,memory,events):
        for address,value in result[1].items():word(memory,address,value)
        for event in result[0]:
            if event[0]=='write':
                _,address,value=event;events.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
    def model(target,args,memory,events):
        state={a:word(memory,a) for a in addresses}
        result=divider_model(*args[:2],table,modules,state) if target==0x10024df8 else dto_model(*args[:3],table,modules,state)
        apply(result,memory,events)
    def program(target,args,memory,events):
        state={a:word(memory,a) for a in addresses}
        if target==0x10024df8:
            result=divide(codes['clock-module-divider-set'],target,*args[:2],table,lookup,state,**leaves)
            assert result==divider_model(*args[:2],table,modules,state);counts[0]+=1
        else:
            result=dto(codes['clock-module-dto-set'],target,*args[:3],table,lookup,state,register_runner=helpers['register_runner'])
            assert result==dto_model(*args[:3],table,modules,state);counts[1]+=1
        apply(result,memory,events)
    if include_other_state:
        from verify_gx8002_clock_init_module_state import verify as combined
        evidence=combined(True,divider_state_runner=program,divider_state_model=model,divider_addresses=sorted(addresses),gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    else:
        evidence=paths(divider_state_runner=program,divider_state_model=model,divider_addresses=sorted(addresses),gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert counts==[2662,570]
    return {'evidence':evidence,'decoded_divider_calls':counts[0],'other_state_included':include_other_state,'decoded_dto_calls':counts[1],'dependency_elf_sha256':hashes,'helpers':helper_evidence,'leaves':leaf_evidence,'source_admitted':False,'limits':['Complete outer call order with decoded divider/DTO programming and decoded lookup/register/divider leaves; full transitions match independent models. Cumulative divider/DTO state, pulse writes and SET/CLR effects merged into outer initialization; other dependency families modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-divider-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_divider_calls'],r['decoded_dto_calls'])
