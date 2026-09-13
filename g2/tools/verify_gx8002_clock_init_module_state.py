# SPDX-License-Identifier: MIT
"""Initialization module switching with cumulative outer register state."""
import json,subprocess,random
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_clock_module_source import execute
from oracle_gx8002_clock_module_source import expected
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word


def verify(include_selectors_voltage=False,divider_state_runner=None,divider_state_model=None,divider_addresses=(),gate_state_runner=None,gate_state_model=None,pll_state_runner=None,pll_state_model=None,copy_runner=None,mode_runner=None,trim_state_runner=None):
    table,context=load();modules={r['module']:r for r in context['modules']};runners,helper_evidence=load_helpers();path=ROOT/'build/gx8002-board/clock-module-source-fixed-candidate.elf';elf=Elf32(path.read_bytes(),'module source');report=json.loads((ROOT/'docs/research/gx8002-clock-module-source-fixed-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));rng=random.Random(671);calls=[]
    addresses=[base+off for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)]
    def apply(result,memory,events):
        for address,value in result[3].items():word(memory,address,value)
        for kind,address,value in result[2]:
            if kind=='write':events.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
    def module(args,memory,events):
        module,source=args[:2];registers={a:word(memory,a) for a in addresses}
        result=execute(code,0x10024be0,module,source,table,modules,registers,**runners)
        assert result==expected(module,source,modules,registers)
        apply(result,memory,events);calls.append((module,source));return result[0]
    def model(module,source,memory,events):
        registers={a:word(memory,a) for a in addresses}
        apply(expected(module,source,modules,registers),memory,events)
    if include_selectors_voltage:
        from verify_gx8002_clock_init_selector_state import verify as combined
        evidence=combined(True,module_state_runner=module,module_state_model=model,divider_state_runner=divider_state_runner,divider_state_model=divider_state_model,divider_addresses=divider_addresses,gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    else:
        evidence=paths(module_state_runner=module,module_state_model=model,divider_state_runner=divider_state_runner,divider_state_model=divider_state_model,divider_addresses=divider_addresses,gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert len(calls)==3610 and len(set(calls))==19
    return {'evidence':evidence,'decoded_module_calls':len(calls),'selectors_voltage_included':include_selectors_voltage,'module_source_pairs':sorted(set(calls)),'dependency_elf_sha256':sha(path.read_bytes()),'helpers':helper_evidence,'source_admitted':False,'limits':['All 19 initialization choices execute corrected source switcher with decoded lookup/register helpers; status and full MMIO transitions match independent model. Module writes and SET/CLR gate effects propagate into cumulative outer state; remaining dependency families are modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-module-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_module_calls'])
