# SPDX-License-Identifier: MIT
"""Clock-switch decoded audio/CPU divider sequence over shared MMIO state."""
import json,random,subprocess
from verify_gx8002_clock_switch_1m import verify as qualify,execute,expected as policy
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from load_gx8002_divider_decoded_helpers import load as load_leaves
from execute_gx8002_clock_module_divider import execute as program
from oracle_gx8002_clock_module_divider import expected
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();table,context=load();modules={r['module']:r for r in context['modules']};helpers,helper_evidence=load_helpers();leaves,leaf_evidence=load_leaves();codes={};hashes={}
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('audio-lowpower-divider','clock-module-divider-set'):
        path=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(path.read_bytes(),name);report=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256'];hashes[name]=sha(path.read_bytes());codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    outer=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text());rng=random.Random(910);cases=0;calls=0
    for index in range(128):
        initial={base+off:rng.getrandbits(32) for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)}
        for module in (7,8,10):
            ptr=modules[module]['divider'];assert ptr
            initial[(0xa0010000 if module<10 else 0xa0300000)+table[ptr]]=0 if index==0 else 0xffffffff if index==1 else rng.getrandbits(32)
        for enable in (0,1,2,0xffffffff):
            state=dict(initial);model=dict(initial);sequence=[]
            def divider(module,value):
                nonlocal state,model,calls
                result=program(codes['clock-module-divider-set'],0x10024df8,module,value,table,lambda m:(0,helpers['lookup_runner'](m)),state,**leaves)
                want=expected(module,value,table,modules,model);assert result==want;state=result[1];model=want[1];sequence.append((module,value));calls+=1
            def audio():
                # Execute the tiny admitted wrapper once at this outer call.
                r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20060000;before=dict(r);pc=0x10025a00
                for _ in range(12):
                    op,args,width=codes['audio-lowpower-divider'][pc];p=[v.strip() for v in args.split(',')]
                    if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
                    elif op=='pop':
                        assert args=='r15';r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==before[f'r{i}'] for i in (*range(4,12),14,15,16,17));return
                    elif op=='movi':r[p[0]]=int(p[1],0)
                    elif op=='bsr':
                        assert int(args,0)==0x10024df8;divider(r['r0'],r['r1'])
                        for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                    else:raise ValueError((op,args))
                    pc+=width
                raise AssertionError('Audio execution bound')
            answers={m:rng.choice((0,1,0xffffffff)) for m in range(11,26)};saved=rng.getrandbits(32)
            result=execute(outer,0x10025a14,answers,saved,enable,(28,0,18,1),divider_runner=divider,audio_runner=audio)
            assert result==policy(answers,saved,enable);assert sequence==[(7,0),(8,0),(10,0)];assert state==model;cases+=1
    return {'evidence':evidence,'cases':cases,'decoded_divider_calls':calls,'dependencies':hashes,'helpers':helper_evidence,'leaves':leaf_evidence,'source_admitted':False,'limits':['Decoded audio wrapper, divider programmer and leaf helpers share MMIO state; independent ordered transition model checked. Private helper frames marshalled. Source selectors, low-power initialization, memcpy and PLL call remain modeled in this integration. Physical timing unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-dividers.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_divider_calls'])
