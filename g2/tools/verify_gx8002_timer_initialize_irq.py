# SPDX-License-Identifier: MIT
"""Timer setup through source IRQ registration and controller enable."""
import json,subprocess
from verify_gx8002_timer_initialize_slots import verify as qualify
from verify_gx8002_timer_initialize import execute,expected,ROOT,decode,Elf32,sha
from compare_gx8002_irq import execute as irq_execute

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/irq/irq.elf'
    report_path=ROOT/'docs/research/gx8002-irq-verification.json';report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'irq')
    for row in report['functions']:
        sec=next(s for s in elf.sections if s['name']==row.get('section_name','.text.'+row['symbol']))
        assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    outer=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True))
    irq=decode(subprocess.check_output([pre,'-d',str(path)],text=True));cases=0
    for hz in (0,999999,1000000,1024000,12288000,24576000,0xffffffff):
      for seed in (0,0xffffffff):
        writes=[]
        def helper(target,args,value):
            if target==0x1002553c:
                assert args==(14,0x100258c4,0)
                for effect in irq_execute(irq,target,*args,enable=0x100254ac):
                    if effect==('enable',14):writes.extend(irq_execute(irq,0x100254ac,14))
                    else:writes.append(effect)
            return value
        assert execute(outer,0x100257e8,hz,seed,helper)==expected(hz)
        assert writes==[(0x20026f64,0x100258c4),(0x20026f68,0),(0xe000e100,1<<14)]
        cases+=1
    return {'evidence':evidence,'irq_elf_sha256':sha(path.read_bytes()),'irq_report_sha256':sha(report_path.read_bytes()),'composed_cases':cases,'source_admitted':False,'limits':['Decoded registration publishes timer handler/private pair and decoded enable writes IRQ14 mask. Separate helper frames; gate and hardware interrupt delivery remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-irq.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
