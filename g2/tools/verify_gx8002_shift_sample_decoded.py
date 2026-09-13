# SPDX-License-Identifier: MIT
"""Execute the actual linked scalar sample helper; not a full-buffer test."""
import json,re
from build_gx8002_backup_shift_q15 import build,ROOT,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_shift_q15_host import expected
MASK=0xffffffff

def signed(value):return value-0x100000000 if value&0x80000000 else value

def execute(code,entry,sample,shift,registers=None):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=sample&65535,r1=shift&MASK)
    if registers is not None:r=registers
    initial=r.copy();pc=entry;condition=False;frames=[]
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            m=re.fullmatch(r'r4-r(\d+), r15',args);assert m,args
            names=[*(f'r{i}' for i in range(4,int(m.group(1))+1)),'r15'];frames.append({k:r[k] for k in names});r['r14']-=4*len(names)
        elif op=='bsr':
            r['r15']=nxt;r=execute(code,int(args,0),0,0,registers=r)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='or':r[p[0]]=r[p[0] if len(p)==2 else p[1]]|r[p[-1]]
        elif op=='sexth':r[p[0]]=((r[p[1]]&65535)-(65536 if r[p[1]]&32768 else 0))&MASK
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op in ('lsl','lsr'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]&31
            r[p[0]]=(a<<b if op=='lsl' else a>>b)&MASK
        elif op=='subu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]-r[p[-1]])&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='nor':r[p[0]]=~(r[p[0] if len(p)==2 else p[1]]|r[p[-1]])&MASK
        elif op=='bmaski':r[p[0]]=(1<<int(p[1]))-1
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmplti':condition=signed(r[p[0]])<int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('max.s32','min.s32'):
            a,b=signed(r[p[1]]),signed(r[p[2]]);r[p[0]]=(max(a,b) if op=='max.s32' else min(a,b))&MASK
        elif op in ('bhsz','blz'):
            if (signed(r[p[0]])>=0)==(op=='bhsz'):nxt=int(p[1],0)
        elif op in ('br','bt','bf'):
            if op=='br' or condition==(op=='bt'):nxt=int(p[0],0)
        elif op in ('rts','pop'):
            if op=='pop':
                saved=frames.pop();r.update(saved);r['r14']+=4*len(saved)
            assert not frames
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return r if registers is not None else r['r0']&65535
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-shift-q15'
    elf=Elf32((out/'shift.elf').read_bytes(),'shift');entry=next(s['value'] for s in elf.symbols() if s['name']=='shift_sample')
    code=decode((out/'shift.disassembly.txt').read_text());cases=0
    for shift in (-1,0,1,15):
        for sample in range(-32768,32768):
            assert execute(code,entry,sample,shift)==expected(sample,shift)&65535,(sample,shift)
            cases+=1
    for shift in (-0x80000000,*range(-40,41),0x7fffffff):
        for sample in (-32768,-32767,-16385,-16384,-2,-1,0,1,2,16383,16384,32766,32767):
            assert execute(code,entry,sample,shift)==expected(sample,shift)&65535,(sample,shift)
            cases+=1
    result={'build':evidence,'helper_entry':entry,'decoded_sample_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Actual compiled scalar helper only; full buffer loop, packed stock instructions and overlapping memory traces not executed here.','Matches explicit scalar interpretation; extreme positive shifts of zero remain unqualified against hardware/vendor undefined behavior.']}
    (ROOT/'docs/research/gx8002-shift-sample-decoded.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['decoded_sample_cases'],'decoded scalar sample cases')
