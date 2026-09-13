# SPDX-License-Identifier: MIT
"""Clock-switch PLL disable through decoded blocking/configuration helpers."""
import json,random,subprocess
from verify_gx8002_clock_switch_1m import verify as qualify,execute,expected
from execute_gx8002_clock_pll_wait import execute as wait
from verify_gx8002_clock_pll import execute as configure,oracle,OFFSETS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=qualify();codes={};hashes={};pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('clock-pll','clock-pll-wait'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(p.read_bytes(),name);r=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text())
        for row in r['functions']:
            s=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(s))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    outer=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text());rng=random.Random(198);cases=0;calls=0
    for enable in (0,1,2,0xffffffff):
        for index in range(128):
            fields=[rng.getrandbits(32) for _ in range(14)];fields[0]=enable;registers={off:rng.getrandbits(32) for off in OFFSETS};perturb=index%3;invocations=[]
            def disable(actual):
                nonlocal calls
                assert actual==0;passed=list(fields);passed[0]=actual;want=oracle(True,passed,registers,perturb)
                def config(value):
                    assert value==0;result=configure(codes['clock-pll'],0x10024b04,True,passed,registers,perturb);assert result==want;invocations.append(result);return result[0]
                result=wait(codes['clock-pll-wait'],0x10025060,actual,0,actual,[],[],pll_runner=config)
                assert result[0]=='return';assert len(invocations)==1
                # Disabled PLL must return without reading a lock or timer: empty
                # scripted input lists make an attempted poll fail the assertion.
                calls+=1
            answers={m:rng.choice((0,1,0xffffffff)) for m in range(11,26)};saved=rng.getrandbits(32)
            result=execute(outer,0x10025a14,answers,saved,enable,(28,0,18,1),pll_runner=disable)
            assert result==expected(answers,saved,enable);assert len(invocations)==int(enable==1);cases+=1
    return {'evidence':evidence,'cases':cases,'decoded_pll_calls':calls,'dependencies':hashes,'source_admitted':False,'limits':['Decoded outer disable, blocking wrapper and configuration routine agree with independent programming oracle; no lock/time poll occurs for disabled PLL. Private parameter/MMIO frames marshalled. Other helpers modeled here; hardware timing remains unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-pll.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_pll_calls'])
