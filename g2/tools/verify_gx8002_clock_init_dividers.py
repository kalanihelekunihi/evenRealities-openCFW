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


def verify():
    table,context=load();modules={r['module']:r for r in context['modules']};helpers,helper_evidence=load_helpers();leaves,leaf_evidence=load_leaves();codes={};hashes={};pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('clock-module-divider-set','clock-module-dto-set'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);r=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text());row=r['functions'][0];s=next(s for s in e.sections if s['name']==row['section_name']);assert sha(e.contents(s))==row['compiled_sha256'];codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    rng=random.Random(551);counts=[0,0]
    def registers(module,kind):
        state={base+off:rng.getrandbits(32) for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)};ptr=modules[module][kind]
        if ptr:state[(0xa0010000 if module<10 else 0xa0300000)+table[ptr]]=rng.getrandbits(32)
        return state
    def lookup(module):return 0,helpers['lookup_runner'](module)
    def divider(module,value):
        state=registers(module,'divider');result=divide(codes['clock-module-divider-set'],0x10024df8,module,value,table,lookup,state,**leaves)
        assert result==divider_model(module,value,table,modules,state);counts[0]+=1
    def set_dto(module,value,enable):
        state=registers(module,'dto');result=dto(codes['clock-module-dto-set'],0x10024f44,module,value,enable,table,lookup,state,register_runner=helpers['register_runner'])
        assert result==dto_model(module,value,enable,table,modules,state);counts[1]+=1
    evidence=paths(divider_runner=divider,dto_runner=set_dto);assert counts==[2662,570]
    return {'evidence':evidence,'decoded_divider_calls':counts[0],'decoded_dto_calls':counts[1],'dependency_elf_sha256':hashes,'helpers':helper_evidence,'leaves':leaf_evidence,'source_admitted':False,'limits':['Complete outer call order with decoded divider/DTO programming and decoded lookup/register/divider leaves; full transitions match independent models. Private snapshots marshalled; shared state integration pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-dividers.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_divider_calls'],r['decoded_dto_calls'])
