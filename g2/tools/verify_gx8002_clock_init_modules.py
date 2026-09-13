# SPDX-License-Identifier: MIT
"""Initialization module clock choices through corrected decoded switcher."""
import json,subprocess,random
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_clock_module_source import execute
from oracle_gx8002_clock_module_source import expected
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode


def verify():
    table,context=load();modules={r['module']:r for r in context['modules']};runners,helper_evidence=load_helpers();path=ROOT/'build/gx8002-board/clock-module-source-fixed-candidate.elf';elf=Elf32(path.read_bytes(),'module source');report=json.loads((ROOT/'docs/research/gx8002-clock-module-source-fixed-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));rng=random.Random(671);calls=[]
    def module(module,source):
        registers={base+off:rng.getrandbits(32) for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)}
        result=execute(code,0x10024be0,module,source,table,modules,registers,**runners)
        assert result==expected(module,source,modules,registers);calls.append((module,source));return result[0]
    evidence=paths(module_runner=module);assert len(calls)==3610 and len(set(calls))==19
    return {'evidence':evidence,'decoded_module_calls':len(calls),'module_source_pairs':sorted(set(calls)),'dependency_elf_sha256':sha(path.read_bytes()),'helpers':helper_evidence,'source_admitted':False,'limits':['All 19 initialization choices execute corrected source switcher with decoded lookup/register helpers; status and full MMIO transitions match independent model. Register snapshots private; combined state propagation remains pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-modules.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_module_calls'])
