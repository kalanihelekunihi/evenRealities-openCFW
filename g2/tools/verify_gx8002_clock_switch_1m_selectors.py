# SPDX-License-Identifier: MIT
"""Decoded clock-switch selector sequence with stateful register helper."""
import json,random,subprocess
from verify_gx8002_clock_switch_1m import verify as qualify,execute,expected
from execute_gx8002_clock_source_select import execute as select
from verify_gx8002_power_initialize import word
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-board/clock-source-select-candidate.elf';elf=Elf32(path.read_bytes(),'selector');report=json.loads((ROOT/'docs/research/gx8002-clock-source-select-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));outer=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text());rng=random.Random(921);cases=0;calls=0
    for initial in [0,0xffffffff]+[1<<i for i in range(32)]+[(1<<i)^0xffffffff for i in range(32)]+[rng.getrandbits(32) for _ in range(62)]:
        for enable in (0,1,2,0xffffffff):
            register=initial;sequence=[]
            def selector(source,clk):
                nonlocal register,calls
                memory={};param=0x20031000;address=0xa001008c;word(memory,param,source);memory[param+4]=clk;word(memory,address,register)
                count=[]
                def helper(target,args,state,events):
                    assert target==0x10024a30 and args==[address,source,clk,1];count.append(args)
                    ret,after,ev=select(code,0x10024a30,args,state,lambda *a:None);assert ret[0]=='return';state.clear();state.update(after);events.extend(ev);return 0
                ret,after,events=select(code,0x10024bcc,[param],memory,helper)
                want=(register&~(1<<source))|(clk<<source);assert ret[0]=='return' and word(after,address)==want and len(count)==1
                assert all(after[k]==v for k,v in memory.items() if not address<=k<address+4)
                register=want;sequence.append((source,clk));calls+=1
            answers={m:rng.choice((0,1,0xffffffff)) for m in range(11,26)};saved=rng.getrandbits(32)
            result=execute(outer,0x10025a14,answers,saved,enable,(28,0,18,1),selector_runner=selector)
            assert result==expected(answers,saved,enable);assert sequence==[(28,0),(18,1)];assert register==(initial&~(1<<28))|(1<<18);cases+=1
    return {'evidence':evidence,'cases':cases,'decoded_selector_calls':calls,'dependency_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Decoded selector and register helper share evolving register state, with independent bit-update checks. Private selector parameter frame marshalled; other helpers modeled here. Hardware timing unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-selectors.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_selector_calls'])
