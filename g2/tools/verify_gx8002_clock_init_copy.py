# SPDX-License-Identifier: MIT
"""Decoded initialization copies from authenticated source data and memcpy."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as paths
from verify_gx8002_memcpy_source import execute,decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha


def verify(include_other_state=False,mode_runner=None,trim_state_runner=None):
    path=ROOT/'build/gx8002-memcpy-source/copy.o';elf=Elf32(path.read_bytes(),'copy');report=json.loads((ROOT/'build/gx8002-memcpy-source/verification.json').read_text());section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_memcpy');assert sha(elf.contents(section))==report['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-dr',str(path)],text=True));calls=[]
    def transfer(memory,dst,src,n):
        assert (src,n) in ((0x10025ce0,20),(0x10025cf4,16))
        # Read the C-generated initializer, not stock bytes as the copy payload.
        owner=Elf32((ROOT/'build/gx8002-board/clock-init-pointer-candidate.elf').read_bytes(),'init');section=next(s for s in owner.sections if s['name']=='.rodata');data=owner.contents(section);offset=src-section['address'];payload=data[offset:offset+n];assert len(payload)==n
        assert bytes(memory[src+i] for i in range(n))==payload
        before=dict(memory);memory.update({src+i:v for i,v in enumerate(payload)})
        ret,trace=execute(code,memory,dst,src,n)
        assert ret==dst and bytes(memory[dst+i] for i in range(n))==payload
        assert all(memory[a]==v for a,v in before.items() if not dst<=a<dst+n)
        assert sorted(a for kind,a in trace if kind=='read')==list(range(src,src+n))
        assert sorted(a for kind,a in trace if kind=='write')==list(range(dst,dst+n));calls.append(n);return ret
    if include_other_state:
        from verify_gx8002_clock_init_pll_state import verify as combined
        evidence=combined(True,copy_runner=transfer,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    else:
        evidence=paths(copy_runner=transfer,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert set(calls)=={16,20}
    return {'evidence':evidence,'decoded_copy_calls':len(calls),'other_state_included':include_other_state,'copy_sizes':sorted(set(calls)),'copy_object_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Decoded source memcpy through complete stock/source initialization paths; source-generated retry and SRAM selector constants copied, bounds and exact byte access coverage checked. Other helpers remain modeled; physical timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-copy.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_copy_calls'])
