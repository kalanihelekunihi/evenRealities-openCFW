#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Scoped decoded lifecycle proof; does not admit the complete transfer function."""
import json,re,subprocess
from analyze_gx8002_dw_spi_quick_transfer import analyze
from build_gx8002_backup_dw_spi_transfer import ROOT,build,IMAGE_SHA,sha,Elf32
from model_gx8002_backup_spi_transfer_lifecycle import Case,expected,DEVICE,MESSAGE
from verify_gx8002_memcpy_source import decode
ADDRESS=0x100082a8
MASK=0xffffffff

def execute(code,case,model=expected,clock_hook=None):
    wanted,depths=model(case)
    events=iter(wanted)
    def event(kind,*args):
        try: item=next(events)
        except StopIteration: raise ValueError('Extra transfer transaction')
        if item[:len(args)+1]!=(kind,*args):
            raise ValueError('Transfer transaction mismatch: '+repr((kind,args,item)))
        return item[-1]
    r={f'r{i}':(0x97123568+i*0x1020304)&MASK for i in range(32)}
    r['r14']=0x2002f7fc
    r['r0']=DEVICE
    r['r1']=MESSAGE
    initial=r.copy()
    frame=code[ADDRESS][1]
    regs=tuple(f'r{i}' for i in range(4,11 if frame=='r4-r10, r15' else 10))+('r15',)
    saved=None
    condition=False
    pc=ADDRESS
    for _ in range(12000):
        op,args,width=code[pc]
        p=[x.strip() for x in args.split(',')]
        nxt=pc+width
        if op=='push':
            if args!=frame or saved is not None: raise ValueError('Transfer frame')
            saved=[r[x] for x in regs]
            r['r14']-=4*len(regs)
        elif op=='pop':
            if args!=frame or saved is None: raise ValueError('Transfer return')
            for reg,value in zip(regs,saved): r[reg]=value
            r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Transfer ABI')
            if next(events,None) is not None: raise ValueError('Missing transfer transaction')
            if r['r0']!=depths: raise ValueError('Transfer return value')
            return depths
        elif op in ('movi','lrw','movih'):
            r[p[0]]=(int(p[1],0)<<(16 if op=='movih' else 0))&MASK
        elif op=='mov': r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
        elif op=='bseti': r[p[0]]|=1<<int(p[1],0)
        elif op=='andi': r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('ld.w','st.w','ld.b','st.b','ld.h','st.h'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match: raise ValueError('Transfer memory operand')
            reg,base,off=match.groups()
            address=(r[base]+int(off,0))&MASK
            kind='8' if op.endswith('.b') else '16' if op.endswith('.h') else ''
            if op.startswith('ld'): r[reg]=event('read'+kind,address)
            else: event('write'+kind,address,r[reg]&(255 if kind else MASK))
        elif op in ('zextb','zexth'): r[p[0]]=r[p[1]]&(255 if op=='zextb' else 65535)
        elif op in ('addu','subu','or','mult'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=r[p[-1]]
            r[p[0]]=(a+b if op=='addu' else a-b if op=='subu' else a|b if op=='or' else a*b)&MASK
        elif op=='and':
            a=r[p[1]] if len(p)==3 else r[p[0]]
            r[p[0]]=a&r[p[-1]]
        elif op=='cmphs': condition=r[p[0]]>=r[p[1]]
        elif op=='min.s32':
            signed=lambda x:x if x<0x80000000 else x-0x100000000
            r[p[0]]=min((r[p[1]],r[p[2]]),key=signed)
        elif op=='mula.32.l': r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op in ('ldr.b','ldr.h','ldr.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match: raise ValueError('Indexed transfer load')
            dest,base,index,shift=match.groups()
            address=(r[base]+(r[index]<<int(shift)))&MASK
            r[dest]=event({'ldr.b':'read8','ldr.h':'read16','ldr.w':'read'}[op],address)
        elif op=='min.u32': r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='cmplt':
            signed=lambda x:x if x<0x80000000 else x-0x100000000
            condition=signed(r[p[0]])<signed(r[p[1]])
        elif op in ('stbi.b','stbi.h','stbi.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not match: raise ValueError('Post-increment transfer store')
            value,base=match.groups()
            size={'stbi.b':1,'stbi.h':2,'stbi.w':4}[op]
            event({1:'write8',2:'write16',4:'write'}[size],r[base],r[value]&((1<<(size*8))-1))
            r[base]=(r[base]+size)&MASK
        elif op=='divu': r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='lsri': r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='inct':
            if condition: r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='cmphsi': condition=r[p[0]]>=int(p[1],0)
        elif op=='max.u32': r[p[0]]=max(r[p[1]],r[p[2]])
        elif op in ('cmpne','cmpnei'):
            condition=r[p[0]]!=(r[p[1]] if op=='cmpne' else int(p[1],0))
        elif op=='incf':
            if not condition: r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='blsz':
            if r[p[0]]==0 or r[p[0]]&0x80000000:nxt=int(p[1],0)
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad': r[p[0]]=(r[p[0]]-1)&MASK
            if (r[p[0]]==0)==(op=='bez'): nxt=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'): nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)
            if target==0x10003be8:
                event('clock',r['r0'],r['r1'])
                if clock_hook is not None: clock_hook(r['r0'],r['r1'])
            else: raise ValueError('Unknown transfer helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}']=(0xa7925693+i*0x113)&MASK
        else: raise ValueError('Unhandled transfer instruction '+op)
        pc=nxt
    raise ValueError('Transfer execution bound')


def programs():
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x40be8','--stop-address=0x40e78',str(path)],text=True));stock={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad','blsz'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        stock[pc+delta]=(op,args,width)
    source=decode((ROOT/'build/gx8002-backup-dw-spi-transfer/dw-spi-quick-transfer-candidate.disassembly.txt').read_text())
    return stock,source

def verify():
    candidate=build();assert candidate['fits'];stock,source=programs()
    cases=[Case(x) for x in (0,MESSAGE,0x2002d000,0xffffffff)]
    for case in cases:execute(stock,case);execute(source,case)
    report={'candidate':candidate,'decoded_cases':len(cases),'source_admitted':False,'limits':['Busy/empty lifecycle only; nonempty transfer paths require separate backup qualification.']}
    (ROOT/'docs/research/gx8002-backup-spi-transfer-lifecycle.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_cases'])
