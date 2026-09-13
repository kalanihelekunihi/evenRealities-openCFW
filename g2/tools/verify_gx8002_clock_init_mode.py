# SPDX-License-Identifier: MIT
"""Initialization branches with decoded startup-mode/reset-reason queries."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as paths
from compare_gx8002_start_mode import execute
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify(include_other_state=False,trim_state_runner=None):
    path=ROOT/'build/gx8002-start-mode/mode.elf';elf=Elf32(path.read_bytes(),'mode');report=json.loads((ROOT/'docs/research/gx8002-start-mode-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));calls=[]
    modeled=[]
    def mode(want):
        if want not in (0,1):
            modeled.append(want);return want
        index=len(calls);bits=0 if want==0 and index%3==0 else 1+(index%15);status=bits|0xfffffff0;raw=0xfffffffe|want;fallback=index&1;discard=0xdeadbeef
        memory={0xa0000034:status,0xa001002c:fallback,0xa0010058:raw,0xa001005c:discard}
        result,trace=execute(code,0x10024984,memory,0x10024940)
        expected_reads=[[0xa0000034,status]]+([[0xa0010058,raw],[0xa001005c,discard]] if bits else [[0xa001002c,fallback]])
        assert result==want and trace==expected_reads;calls.append(bits);return result
    if include_other_state:
        from verify_gx8002_clock_init_copy import verify as combined
        evidence=combined(True,mode_runner=mode,trim_state_runner=trim_state_runner)
    else:
        evidence=paths(mode_runner=mode,modes=(0,1),trim_state_runner=trim_state_runner)
    assert len(calls)==96
    assert len(modeled)==(96 if include_other_state else 0)
    return {'evidence':evidence,'decoded_mode_calls':len(calls),'modeled_invalid_mode_calls':len(modeled),'other_state_included':include_other_state,'status_low_bits_covered':sorted(set(calls)),'mode_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Full initialization stock/source/oracle paths driven by decoded startup-mode and reset-reason bodies; ordered MMIO reads checked. Register inputs scripted; invalid mode values injected only for defensive outer coverage, not claimed as decoded query outputs. Other helpers depend on composition option; hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-mode.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_mode_calls'])
