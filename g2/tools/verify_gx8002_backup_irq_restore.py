# SPDX-License-Identifier: MIT
"""Authenticate complete restore body and compare ordered memory operations."""
import json,re,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_double_wrapper_references import analyze


def execute(code,entry,first,second):
    regs={f'r{i}':0xabc00000+i for i in range(32)};initial=dict(regs)
    memory={0x200173a0:first,0x200173a4:second};events=[];pc=entry
    for _ in range(20):
        op,args,width=code[pc]
        if op=='lrw':
            reg,value=args.split(',');regs[reg.strip()]=int(value,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,offset=m.groups();address=regs[base]+int(offset,0)
            if op=='ld.w':
                assert address in memory;value=memory[address];regs[reg]=value;events.append(['read',address,value])
            else:
                assert address in (0xe000e100,0xe000e104);events.append(['write',address,regs[reg]])
        elif op=='rts':
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            return events
        else:raise AssertionError((hex(pc),op,args))
        pc+=width
    raise AssertionError('instruction bound')


def verify():
    report=json.loads((ROOT/'docs/research/gx8002-backup-irq-restore.json').read_text())
    path=ROOT/'build/gx8002-backup-irq-restore/restore.elf'
    assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'restore');sec=next(s for s in elf.sections if s['name']=='.text')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    body=elf.contents(sec);assert body==stock[0x3d16c:0x3d184]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    oldelf=Elf32(wrapper.read_bytes(),'stock');assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d16c','--stop-address=0x3d17a',str(wrapper)],text=True))
    masks=[0,0xffffffff,*[1<<i for i in range(32)],*[0xffffffff^(1<<i) for i in range(32)]]
    pairs=[(a,0xa55a1234) for a in masks]+[(0x5aa54321,a) for a in masks]
    rng=random.Random(804);pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(32)]
    for a,b in pairs:
        expected=[['read',0x200173a0,a],['write',0xe000e100,a],['read',0x200173a4,b],['write',0xe000e104,b]]
        assert execute(source,0x1000482c,a,b)==execute(old,0x3d16c,a,b)==expected
    refs=analyze(0x3d16c,0x3d184,require_entry_only=False)
    result={'elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'complete_body_stock_identical':True,'ordered_access_cases':len(pairs),'references':refs,'source_admitted':False,'limits':['Decoded reads and writes, order and preserved ABI registers verified. Physical interrupt-controller effects and asynchronous interrupts are not modeled.','The two-word BSS reader is known; its writers and computed access paths still require closure before relocation.']}
    (ROOT/'docs/research/gx8002-backup-irq-restore-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['ordered_access_cases'],r['references'])
