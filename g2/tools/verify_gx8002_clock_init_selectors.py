# SPDX-License-Identifier: MIT
"""Complete initialization selector calls through decoded register updates."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify():
    path=ROOT/'build/gx8002-board/clock-source-select-candidate.elf';elf=Elf32(path.read_bytes(),'selector');r=json.loads((ROOT/'docs/research/gx8002-clock-source-select-source-verification.json').read_text())
    for row in r['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));calls=[]
    def selector(source,clk):
        initial=(0,0xffffffff,0xaaaaaaaa,0x55555555)[len(calls)%4];memory={};param=0x20031000;address=0xa001008c;word(memory,param,source);memory[param+4]=clk;word(memory,address,initial);invoked=[]
        def helper(target,args,state,events):
            assert target==0x10024a30 and args==[address,source,clk,1];invoked.append(True)
            ret,after,ev=execute(code,target,args,state,lambda *a:None);assert ret[0]=='return';state.clear();state.update(after);events.extend(ev);return 0
        ret,after,events=execute(code,0x10024bcc,[param],memory,helper)
        want=(initial&~(1<<source))|((clk<<source)&0xffffffff)
        assert ret[0]=='return' and word(after,address)==want and invoked==[True]
        assert all(after[k]==v for k,v in memory.items() if not address<=k<address+4);calls.append((source,clk))
    evidence=paths(selector_runner=selector);assert len(calls)==556
    return {'evidence':evidence,'decoded_selector_calls':len(calls),'selector_pairs':sorted(set(calls)),'dependency_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Every outer selector call executes decoded selector/register helper with independent bit-update checks and preserved parameter bytes. Private register snapshots marshalled; combined MMIO propagation remains pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-selectors.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_selector_calls'])
