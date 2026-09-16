# SPDX-License-Identifier: MIT
"""Decoded mode initialization with callback-driven state changes and ABI checks."""
import json,re,subprocess,itertools
from build_gx8002_backup_mode import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
LOOP=0x2002d2b4
INDEX=LOOP+4
RECORDS=(0x1001366c,0x100136b0)


def execute(code,entry,requested,changes,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r['r0']=requested;r['r14']=0x20070000;initial=r.copy()
    memory={LOOP:seed,INDEX:seed,0x10013664:RECORDS[0],0x10013668:RECORDS[1]}
    for i,address in enumerate(RECORDS):
        memory.update({address:5*i,address+4:0x11000000+i*32,address+16:0x11000010+i*32})
    trace=[];calls=0;pc=entry;condition=False;saved=None
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r5, r15';saved={k:r[k] for k in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            assert args=='r4-r5, r15';r.update(saved);r['r14']+=12
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],memory[LOOP],memory[INDEX],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('br','bf','bt'):
            if op=='br' or (op=='bt' and condition) or (op=='bf' and not condition):nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            dest,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
            if op=='ld.w':r[dest]=memory[address]
            else:
                assert address in (LOOP,INDEX);memory[address]=r[dest];trace.append(('write',address,r[dest]))
        elif op=='ldr.w':
            dest,base,index,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();r[dest]=memory[r[base]+(r[index]<<int(shift))]
        elif op=='jsr':
            target=r[p[0]];assert calls<2
            expected_kind=16 if calls==0 else 0
            assert target in (0x11000000+expected_kind,0x11000020+expected_kind)
            trace.append(('call',target,None if calls==0 else r['r0']))
            change=changes[calls]
            if change is not None:memory[INDEX]=change
            memory[LOOP]=(seed+calls)&0xffffffff
            calls+=1
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((pc,op,args))
        pc=nxt
    raise AssertionError('Execution bound')


def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0x44088','--stop-address=0x440e0',str(path)],text=True))
    source=decode((ROOT/'build/gx8002-backup-mode/mode.disassembly.txt').read_text());cases=0
    for requested,a,b,seed in itertools.product((0,1,5,6,0xffff,0xffffffff),(None,0,1),(None,0,1),(0,1,0x12345678,0xffffffff)):
        result=execute(source,0x1000b748,requested,(a,b),seed)
        assert result==execute(stock,0x44088,requested,(a,b),seed)
        selected=int(requested==5);second=selected if a is None else a;final=second if b is None else b
        assert result[:3]==(5*final,(seed+1)&0xffffffff,final)
        assert [event for event in result[3] if event[0]=='call']==[('call',0x11000010+32*selected,None),('call',0x11000000+32*second,0xffff)]
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Two immutable mode records; callbacks may change index to either valid mode and loop state. Callback bodies modeled, volatile register clobbering enforced. Asynchronous mutation, invalid indices and full firmware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-mode-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'])
