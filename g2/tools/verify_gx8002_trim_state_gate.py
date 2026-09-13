# SPDX-License-Identifier: MIT
"""Decoded trim query, enable wrapper and platform gate programming."""
import json,subprocess
from verify_gx8002_trim_state import verify as qualify
from compare_gx8002_platform_gate import execute,oracle
from load_gx8002_clock_context import load,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode


def verify():
    memory,context=load();table=bytes(memory[0x200266e0+i] for i in range(416));path=ROOT/'build/gx8002-platform-gate/gate-fit.elf';elf=Elf32(path.read_bytes(),'gate');report=json.loads((ROOT/'docs/research/gx8002-platform-gate-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'));pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));calls=[]
    def gate(module,enable,value):
        assert (module,enable)==(9,1)
        trace=execute(code,0x10025080,jumps,table,module,enable,value,0)
        assert trace==oracle(table,module,enable,value);calls.append(trace)
    evidence=qualify(gate);assert len(calls)==260
    return {'evidence':evidence,'decoded_gate_calls':len(calls),'gate_elf_sha256':sha(path.read_bytes()),'context':context,'source_admitted':False,'limits':['Query, wrapper and gate code decoded in order; gate MMIO trace matches independent model using authenticated source descriptors. Gate lookup/private stack abstracted as in admitted gate qualification. Physical timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-trim-state-gate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_gate_calls'])
