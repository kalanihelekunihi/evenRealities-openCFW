# SPDX-License-Identifier: MIT
"""Compare full decoded clock control flow; low-level hardware helpers modeled."""
import json
import random
import re
import subprocess
from itertools import product
from build_gx8002_backup_clock_initialize import build
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode

MASK=0xffffffff
PLL=0x200168c0
GATES=0x20017394


def execute(code,entry,helpers,memory,start,trim,stage,success,seed):
    rng=random.Random(seed);r={f'r{i}':rng.getrandbits(32) for i in range(32)}
    r['r14']=0x20040000;r['r15']=0xfffffff0;initial=dict(r)
    mem=dict(memory);trace=[];pc=entry;condition=False;attempt=0;depth=0
    def write(address,value,size=4):
        for i in range(size):mem[address+i]=(value>>(8*i))&255
    def read(address,size=4):return sum(mem[address+i]<<(8*i) for i in range(size))
    write(0xa0005058,seed);write(0xa0010030,(seed&~1)|(trim&1));write(PLL+56,stage);write(GATES,seed);write(0xa0005084,seed);write(0xa0005060,seed^MASK)
    def registers(args):
        result=[]
        for part in args.split(', '):
            if '-' in part:
                a,b=part.split('-');result.extend(f'r{i}' for i in range(int(a[1:]),int(b[1:])+1))
            else:result.append(part)
        return result
    for steps in range(2000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            regs=registers(args)
            if op=='push':
                r['r14']-=4*len(regs)
                for i,reg in enumerate(regs):write(r['r14']+4*i,r[reg])
            else:
                for i,reg in enumerate(regs):r[reg]=read(r['r14']+4*i)
                r['r14']+=4*len(regs);nxt=r['r15']
                if depth==0:
                    assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
                    return trace,'return'
                depth-=1
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='rts':
            assert depth>0;depth-=1;nxt=r['r15']
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','andi','andni','ori','lsli','lsr'):
            left=r[p[0] if len(p)==2 else p[1]];right=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(left-right if op=='subi' else left&right if op=='andi' else left|right if op=='ori' else left&~right if op=='andni' else left<<right if op=='lsli' else left>>(right&31) if op=='lsr' else left+right)&MASK
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op in ('ld.w','st.w','st.b','ldr.w','ldbi.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+|r\d+ << 2))?\)',args);assert m,(op,args)
            reg,base,offset=m.groups();address=r[base]
            if offset:address+=(r[offset.split()[0]]<<2) if '<<' in offset else int(offset,0)
            observed=address in (PLL+20,PLL+56,GATES,0xa0005084,0xa0005060,0xa0010030,0xa0005058)
            if op.startswith('st'):
                write(address,r[reg],1 if op=='st.b' else 4)
                if observed:trace.append(['write',address,r[reg]])
            else:
                r[reg]=read(address)
                if observed:trace.append(['read',address,r[reg]])
            if op=='ldbi.w':r[base]+=4
        elif op in ('cmpne','cmpnei'):condition=r[p[0]]!=(r[p[1]] if p[1] in r else int(p[1],0))
        elif op in ('br','bt','bf','bez','bnez'):
            take=op=='br' or (op=='bt' and condition) or (op=='bf' and not condition)
            if op in ('bez','bnez'):take=(r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
            if nxt==pc:return trace,'failure-loop'
        elif op=='bsr':
            target=int(args,0)
            if target not in helpers:
                assert target in code;r['r15']=nxt;nxt=target;depth+=1
            else:
                name=helpers[target];value=0
                if name=='source':parameters=[read(r['r0']),read(r['r0']+4,1)]
                elif name in ('pll','retry'):parameters=[r['r0'],read(PLL+20)]+([r['r1']] if name=='retry' else [])
                else:parameters=[r[f'r{i}'] for i in range({'ldo':1,'div':2,'dto':3,'module':2,'gate':2,'preserve':0,'trim':0}[name])]
                trace.append(['call',name,*parameters])
                if name=='preserve':value=start
                elif name=='trim':value=trim
                elif name=='retry':
                    value=0 if attempt==success else MASK;write(PLL+20,0xdeadbeef+attempt);attempt+=1
                elif name=='gate':write(GATES,(read(GATES)*1664525+1013904223)&MASK)
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=rng.getrandbits(32)
                r['r0']=value
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('clock execution bound')


def verify():
    result=build();path=ROOT/'build/gx8002-backup-clock-initialize/clock.elf';elf=Elf32(path.read_bytes(),'clock')
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';wrapped=Elf32(wrapper.read_bytes(),'stock')
    assert wrapped.contents(next(s for s in wrapped.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3bbd4','--stop-address=0x3be14',str(wrapper)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True));memory={}
    for section in elf.sections:
        if section['flags']&2:
            memory.update({section['address']+i:b for i,b in enumerate(elf.contents(section))})
    names={'gx_clock_set_div':'div','gx_clock_set_dto':'dto','gx_clock_set_module_source':'module','gx_clock_set_source':'source','gx_clock_set_pll':'pll','gx_clock_set_pll_no_block':'retry','gx_clock_set_module_enable':'gate','open_cfw_gx8002_backup_preserve_memory':'preserve','open_cfw_gx8002_backup_trim_state':'trim','open_cfw_gx8002_backup_ldo_control':'ldo'}
    helpers={offset:names[name] for name,offset in result['absolute_bindings_package_offsets'].items()}
    mapped={address-0x3b940+0x10003000:name for address,name in helpers.items()}
    # Assert the linked symbols resolve to the same image mapping, independently of the executor.
    symbols={s['name']:s['value'] for s in elf.symbols()}
    for name,offset in result['absolute_bindings_package_offsets'].items():assert symbols[name]==offset-0x3b940+0x10003000
    cases=0
    for start,trim,stage,success,seed in product((0,1,2,MASK),(0,1,2),(0,1,MASK),range(6),(0,0x87654321)):
        a=execute(old,0x3bbd4,helpers,memory,start,trim,stage,success,seed)
        b=execute(new,result['entry_address'],mapped,memory,start,trim,stage,success,seed)
        assert a==b,(start,trim,stage,success,seed,a,b)
        assert b[1]==('failure-loop' if start==0 and trim==1 and success==5 else 'return')
        calls=[e for e in b[0] if e[0]=='call']
        assert calls[:3]==[['call','ldo',2],['call','div',6,2],['call','preserve']]
        if b[1]=='return':
            assert calls[-1]==['call','ldo',2]
            assert len([e for e in calls if e[1]=='module'])==19
            assert len([e for e in calls if e[1]=='gate'])==(16 if start==1 else 1)
        cases+=1
    from build_gx8002_backup_trim_state import build as build_trim
    trim_evidence=build_trim();trim_path=ROOT/'build/gx8002-backup-trim-state/trim.elf'
    trim_elf=Elf32(trim_path.read_bytes(),'trim reader')
    trim_body=trim_elf.contents(next(s for s in trim_elf.sections if s['name']=='.text'))
    assert trim_body==stock[0x3c95c:0x3c972]
    old.update(decode(subprocess.check_output([pre,'-D','--start-address=0x3c95c','--stop-address=0x3c972',str(wrapper)],text=True)))
    new.update(decode(subprocess.check_output([pre,'-d',str(trim_path)],text=True)))
    real_helpers={a:n for a,n in helpers.items() if n!='trim'}
    real_mapped={a:n for a,n in mapped.items() if n!='trim'}
    trim_cases=0
    for start,trim,stage,success,seed in product((0,1,2,MASK),(0,1),(0,1,MASK),range(6),(0,0x87654321)):
        a=execute(old,0x3bbd4,real_helpers,memory,start,trim,stage,success,seed)
        b=execute(new,result['entry_address'],real_mapped,memory,start,trim,stage,success,seed)
        assert a==b,(start,trim,stage,success,seed)
        reads=[e for e in b[0] if e[:2]==['read',0xa0010030]]
        assert reads==([['read',0xa0010030,(seed&~1)|trim]] if start==0 else [])
        assert b[1]==('failure-loop' if start==0 and trim==1 and success==5 else 'return')
        trim_cases+=1
    from verify_gx8002_backup_ldo_control import verify as verify_ldo
    ldo_evidence=verify_ldo();ldo_path=ROOT/'build/gx8002-backup-ldo-control/ldo.elf'
    old.update(decode(subprocess.check_output([pre,'-D','--start-address=0x40a34','--stop-address=0x40a74',str(wrapper)],text=True)))
    new.update(decode(subprocess.check_output([pre,'-d',str(ldo_path)],text=True)))
    real_helpers={a:n for a,n in real_helpers.items() if n!='ldo'}
    real_mapped={a:n for a,n in real_mapped.items() if n!='ldo'}
    ldo_cases=0
    for start,trim,stage,success,seed in product((0,1,2,MASK),(0,1),(0,1,MASK),range(6),(0,0x87654321)):
        a=execute(old,0x3bbd4,real_helpers,memory,start,trim,stage,success,seed)
        b=execute(new,result['entry_address'],real_mapped,memory,start,trim,stage,success,seed)
        assert a==b,(start,trim,stage,success,seed)
        value=(seed&255)|6
        effects=[e for e in b[0] if len(e)>1 and e[1]==0xa0005058]
        expected=[['read',0xa0005058,seed],['write',0xa0005058,value]]
        if b[1]=='return':expected+=[['read',0xa0005058,value],['write',0xa0005058,value]]
        assert effects==expected
        ldo_cases+=1
    return {'composed_ldo_cases':ldo_cases,'ldo_evidence':ldo_evidence,'composed_trim_cases':trim_cases,'trim_evidence':trim_evidence,'cases':cases,'build':result,'limits':['Entire stock initializer and linked source setup/retry helpers execute in one register/memory frame. Low-level hardware/predicate helpers are modeled, including mutation of PLL feedback divider and gate bitmap. No hardware timing, incoming-reference or firmware integration qualification.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-clock-initialize-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'complete clock cases passed')
