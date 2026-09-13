# SPDX-License-Identifier: MIT
"""Timer initializer composed with decoded module-23 gate programming."""
import json,subprocess
from verify_gx8002_timer_initialize_irq import verify as qualify
from verify_gx8002_timer_initialize import execute,expected,ROOT,decode,Elf32,sha
from compare_gx8002_platform_gate import execute as gate,oracle
from load_gx8002_clock_context import load

def verify():
    evidence=qualify();memory,context=load();table=bytes(memory[0x200266e0+i] for i in range(416))
    path=ROOT/'build/gx8002-platform-gate/gate-fit.elf';report_path=ROOT/'docs/research/gx8002-platform-gate-verification.json'
    report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'gate')
    for row in report['functions']:
        sec=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'))
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    outer=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True));cases=0
    for selection in (0,1,0xffffffff,0x12345678):
      for hz in (0,1024000,24576000,0xffffffff):
        calls=[]
        def helper(target,args,value):
            if target==0x10025080:
                assert args==(23,1)
                trace=gate(code,target,jumps,table,23,1,selection,0)
                assert trace==oracle(table,23,1,selection);calls.append(trace)
            return value
        assert execute(outer,0x100257e8,hz,selection,helper)==expected(hz) and len(calls)==1
        cases+=1
    return {'evidence':evidence,'context':context,'gate_elf_sha256':sha(path.read_bytes()),'gate_report_sha256':sha(report_path.read_bytes()),'composed_cases':cases,'source_admitted':False,'limits':['Decoded module-23 gate programming composed at actual outer call; authenticated descriptors and independent ordered gate-write oracle. Gate lookup/private frame abstracted as in admitted gate qualification. Separate dependency frames and scripted register inputs; shared hardware-state/lifecycle qualification pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-gate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
