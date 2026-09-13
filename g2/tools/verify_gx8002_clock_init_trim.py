# SPDX-License-Identifier: MIT
"""Initialization ROM branch through admitted decoded trim query/wrapper."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_trim_state import execute
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify(include_other_state=False):
    codes={};hashes={};pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('trim-state','trim-clock-enable'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);r=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text());row=r['functions'][0];s=next(s for s in e.sections if s['name']==row['section_name']);assert sha(e.contents(s))==row['compiled_sha256'];hashes[name]=sha(p.read_bytes());codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    calls=[]
    def trim(want):
        value=(0,0xfffffffe,0xaaaaaaaa)[len(calls)%3]|want
        result,trace=execute(codes,value)
        assert result==want and trace==[('gate',9,1),('read',0xa0010030,value)];calls.append(trace);return result
    modeled=[]
    def shared(want,memory,events,gate):
        if want not in (0,1):modeled.append(want);return want
        value=(0,0xfffffffe,0xaaaaaaaa)[len(calls)%3]|want
        def program(module,enable,ignored):
            assert gate is not None
            gate([module,enable],memory,events)
        result,trace=execute(codes,value,program)
        assert result==want and trace==[('gate',9,1),('read',0xa0010030,value)]
        calls.append(trace);return result
    if include_other_state:
        from verify_gx8002_clock_init_mode import verify as combined
        evidence=combined(True,trim_state_runner=shared)
    else:
        evidence=paths(trim_runner=trim,trims=(0,1))
    assert len(calls)==24
    assert len(modeled)==(24 if include_other_state else 0)
    return {'evidence':evidence,'decoded_trim_calls':len(calls),'modeled_invalid_trim_calls':len(modeled),'other_state_included':include_other_state,'dependency_elf_sha256':hashes,'source_admitted':False,'limits':['Full initialization branch driven by decoded trim query and wrapper, with ordered gate request then masked read. Combined option routes gate programming into outer shared state; invalid trim values explicitly injected only for defensive branches. Trim register input scripted; hardware and frame limitations remain.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-trim.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_trim_calls'])
