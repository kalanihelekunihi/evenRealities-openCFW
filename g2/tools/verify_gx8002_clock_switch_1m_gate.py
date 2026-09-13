# SPDX-License-Identifier: MIT
"""Clock-switch gate accumulation with decoded corrected gate-query source."""
import json,subprocess,random
from verify_gx8002_clock_switch_1m import verify as qualify,execute,expected
from execute_gx8002_clock_gate_query import execute as query
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=qualify();table,context=load();modules={r['module']:r for r in context['modules']};helpers,helper_evidence=load_helpers()
    path=ROOT/'build/gx8002-board/clock-gate-query-fixed-candidate.elf';elf=Elf32(path.read_bytes(),'gate query')
    report=json.loads((ROOT/'docs/research/gx8002-clock-gate-query-fixed-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));outer=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text());rng=random.Random(751);cases=0;calls=0
    words=[0,0xffffffff]+[1<<i for i in range(32)]+[(1<<i)^0xffffffff for i in range(32)]+[rng.getrandbits(32) for _ in range(62)]
    for value in words:
        state={0xa0010018:value,0xa0300018:value};answers={}
        for module in range(11,26):
            offsets=[modules[module+i]['gate_all_offset'] for i in (1,2)] if module in (16,19,22) else [modules[module]['gate_all_offset']]
            answers[module]=0xffffffff if modules[module]['gate_all_offset']==0 else int(any(not ((value>>(off&31))&1) for off in offsets))
        def gate(module):
            nonlocal calls
            result,trace=query(code,0x10025180,module,table,lambda m:(0,helpers['lookup_runner'](m)),state)
            assert result==answers[module]
            expected_trace=[('lookup',module,0)]
            if modules[module]['gate_all_offset']!=0:expected_trace.append(('read',0xa0300018,value))
            assert trace==expected_trace;calls+=1;return result
        for saved in (0,rng.getrandbits(32),0xffffffff):
            for enable in (0,1,2,0xffffffff):
                result=execute(outer,0x10025a14,{},saved,enable,(28,0,18,1),gate)
                assert result==expected(answers,saved,enable);cases+=1
    return {'evidence':evidence,'cases':cases,'decoded_gate_calls':calls,'gate_elf_sha256':sha(path.read_bytes()),'helpers':helper_evidence,'source_admitted':False,'limits':['Corrected gate query and lookup decoded through clock-switch accumulation; private helper frames marshalled. Other clock-switch helpers remain modeled, and physical timing is unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-gate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_gate_calls'])
