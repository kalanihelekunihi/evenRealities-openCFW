# SPDX-License-Identifier: MIT
"""Compose timer setup with decoded memset over the source-owned timer slots."""
import json,subprocess
from verify_gx8002_timer_initialize_channel import verify as qualify
from verify_gx8002_timer_initialize import execute,expected,ROOT,decode,Elf32,sha
from compare_gx8002_memset import execute as fill,expected as fill_expected

def verify():
    evidence=qualify();owners={}
    for kind,filename in (('memset','memset.elf'),('timer-dispatch','timer-dispatch.elf')):
        path=ROOT/'build/gx8002-source-candidate'/kind/filename
        report_path=ROOT/'docs/research'/('gx8002-memset-verification.json' if kind=='memset' else 'gx8002-timer-dispatch-source-verification.json')
        report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),kind)
        for row in report['functions']:
            sec=next(s for s in elf.sections if s['name']==row['section_name'])
            assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
        owners[kind]={'elf_sha256':sha(path.read_bytes()),'report_sha256':sha(report_path.read_bytes())}
        if kind=='timer-dispatch':
            state=next(s for s in elf.sections if s['address']==0x20026d84)
            assert state['type']==8 and state['size']==360 and state['flags']&2
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    outer=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True))
    memset=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-source-candidate/memset/memset.elf')],text=True))
    cases=0
    for pattern in (0,1,0x55,0xaa,0xff):
      for hz in (0,1000000,24576000,0xffffffff):
        memory={a:pattern for a in range(0x20026d80,0x20026ef0)};before=memory.copy();calls=[]
        def helper(target,args,value):
            if target==0x102099cc:
                assert args==(0x20026d84,0,360)
                result=fill(memset,target,*args,seed=pattern)
                assert result==fill_expected(*args)
                for address,width,word in result['trace']:
                    for i in range(width):memory[address+i]=(word>>(8*i))&255
                calls.append(result);return result['result']
            if target==0x1002553c:
                assert all(memory[a]==0 for a in range(0x20026d84,0x20026eec))
            return value
        assert execute(outer,0x100257e8,hz,pattern,helper)==expected(hz) and len(calls)==1
        assert memory=={a:(0 if 0x20026d84<=a<0x20026eec else v) for a,v in before.items()}
        cases+=1
    return {'evidence':evidence,'owners':owners,'composed_cases':cases,'slot_address':0x20026d84,'slot_bytes':360,'source_admitted':False,'limits':['Actual decoded memset stores applied to shared modeled memory before IRQ registration, with adjacent guard bytes preserved. Slot allocation authenticated from source-dispatch NOBITS section. Gate/IRQ effects and hardware remain separate qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-slots.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
