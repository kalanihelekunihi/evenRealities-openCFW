# SPDX-License-Identifier: MIT
"""Execute stock inline retry and complete rebuilt helper against a setter model."""
import json
import re
import subprocess
from itertools import product
from build_gx8002_backup_pll_retry import build
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode

MASK=0xffffffff
PLL=0x200168c0


def execute(code, entry, stop, setter, memory, original, success, failure, mutation, seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=1,r5=0,r14=0x20040000)
    initial=dict(r);mem=dict(memory);mem[PLL+20]=original;mem[PLL+56]=MASK
    trace=[];frames=[];pc=entry;condition=False
    for _ in range(300):
        if pc==stop:return trace,mem,'success'
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];next_pc=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu'):
            left=r[p[0] if len(p)==2 else p[1]];v=p[-1];right=r[v] if v.startswith('r') else int(v,0)
            r[p[0]]=(left+(-right if op=='subi' else right))&MASK
        elif op in ('st.w','ld.w','ldr.w','ldbi.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+|r\d+ << 2))?\)',args);assert m,(op,args)
            reg,base,offset=m.groups();address=r[base]
            if offset:address+=(r[offset.split()[0]]<<2) if '<<' in offset else int(offset,0)
            if op=='st.w':
                mem[address]=r[reg]
                if PLL<=address<PLL+60:trace.append(['write',address,r[reg]])
            else:r[reg]=mem[address]
            if op=='ldbi.w':r[base]=(r[base]+4)&MASK
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bf','bt','bez','bnez'):
            take=op=='br' or (op=='bf' and not condition) or (op=='bt' and condition)
            if op in ('bez','bnez'):take=(r[p[0]]==0)==(op=='bez')
            if take:next_pc=int(p[-1],0)
            if next_pc==pc:return trace,mem,'failure-loop'
        elif op=='bsr':
            assert int(args,0)==setter
            index=sum(e[0]=='setter' for e in trace)
            trace.append(['setter',r['r0'],r['r1'],mem[PLL+20],mem[PLL+56]])
            if mutation:mem[PLL+20]=(0xdeadbeef+index)&MASK
            for i in (0,1,2,3,12,13):r[f'r{i}']=(seed^0x12345678^i)&MASK
            r['r0']=0 if index==success else failure
        elif op=='push':
            assert args=='r4-r8, r15';frames.append({k:r[k] for k in ('r4','r5','r6','r7','r8','r15')});r['r14']-=24
        elif op=='pop':
            assert args=='r4-r8, r15';r.update(frames.pop());r['r14']+=24
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in range(4,12)) and r['r14']==initial['r14'] and r['r15']==initial['r15']
            return trace,mem,'success'
        else:raise ValueError((hex(pc),op,args))
        pc=next_pc
    raise AssertionError('execution bound')


def verify():
    report=build();out=ROOT/'build/gx8002-backup-pll-retry';elf=Elf32((out/'retry.elf').read_bytes(),'retry')
    memory={}
    for sec in elf.sections:
        if sec['flags']&2:
            data=elf.contents(sec)
            for i in range(0,len(data)-3,4):memory[sec['address']+i]=int.from_bytes(data[i:i+4],'little')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapped=Elf32(wrapper.read_bytes(),'stock');assert wrapped.contents(next(s for s in wrapped.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3bd9e','--stop-address=0x3bde8',str(wrapper)],text=True))
    new=decode((out/'retry.disassembly.txt').read_text());cases=0
    for original,success,failure,mutation,seed in product((0,1,10,15,3071,0xfffffff5,MASK),range(6),(1,2,MASK),(False,True),(0,0x87654321)):
        a=execute(old,0x3bd9e,0x3bde8,0x3c334,memory,original,success,failure,mutation,seed)
        b=execute(new,0x10018000,None,0x100039f4,memory,original,success,failure,mutation,seed)
        assert a[0]==b[0] and a[2]==b[2]
        count=min(success+1,5);adjustments=(0,10,15,-10,-15)
        expected=[['write',PLL+56,1]]
        for i in range(count):
            value=(original+adjustments[i])&MASK
            expected.extend([['write',PLL+20,value],['setter',PLL,40,value,1]])
        assert b[0]==expected and b[2]==('success' if success<5 else 'failure-loop')
        assert a[1][PLL+20]==b[1][PLL+20] and a[1][PLL+56]==b[1][PLL+56]==1
        cases+=1
    return {'cases':cases,'build':report,'limits':['Setter outcomes and divider mutations are modeled; setter hardware body is not executed. Stock scope is its inline retry region; source helper return ABI is checked. Terminal failure is recognized only at an executed self-branch. Not integrated or hardware qualified.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-pll-retry-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'PLL retry cases passed')
