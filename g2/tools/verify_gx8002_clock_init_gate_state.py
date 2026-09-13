# SPDX-License-Identifier: MIT
"""Decoded initialization gate restoration and I2C gate programming."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as qualify
from compare_gx8002_platform_gate import execute,oracle
from load_gx8002_clock_context import load,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word


def verify(pll_state_runner=None,pll_state_model=None,copy_runner=None,mode_runner=None,trim_state_runner=None):
    memory,context=load();table=bytes(memory[0x200266e0+i] for i in range(416));path=ROOT/'build/gx8002-platform-gate/gate-fit.elf';elf=Elf32(path.read_bytes(),'gate');report=json.loads((ROOT/'docs/research/gx8002-platform-gate-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'));pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));calls=[]
    def apply(trace,state,events):
        for item in trace:
            if item[0]!='write':continue
            _,address,value=item;word(state,address,value)
            events.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
            normal=(address&~255)+0x18;previous=word(state,normal)
            word(state,normal,(previous|value) if address&255==0x1c else previous&~value&0xffffffff)
    def model(module,enable,state,events):
        value=word(state,0xa001008c if module<10 else 0xa0300088)
        apply(oracle(table,module,enable,value),state,events)
    def gate(args,state,events):
        module,enable=args[:2];assert module in (5,9) or 11<=module<26
        value=word(state,0xa001008c if module<10 else 0xa0300088)
        trace=execute(code,0x10025080,jumps,table,module,enable,value,0)
        assert trace==oracle(table,module,enable,value);apply(trace,state,events);calls.append(trace)
    from verify_gx8002_clock_init_divider_state import verify as combined
    evidence=combined(True,gate_state_runner=gate,gate_state_model=model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner);assert len(calls)==(934 if trim_state_runner else 910)
    return {'evidence':evidence,'decoded_gate_calls':len(calls),'gate_elf_sha256':sha(path.read_bytes()),'context':context,'source_admitted':False,'limits':['Combined initialization shared state includes gate restoration and hardware-I2C enable through decoded gate programming; gate MMIO trace matches independent model using authenticated source descriptors. Gate lookup/private stack abstracted as in admitted gate qualification. Physical timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-gate-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_gate_calls'])
