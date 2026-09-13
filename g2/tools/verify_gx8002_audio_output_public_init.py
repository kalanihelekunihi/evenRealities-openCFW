# SPDX-License-Identifier: MIT
"""Decoded public-init global rereads, indirect ABI and diagnostic arguments."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_public_init import build,ROOT,IMAGE,sha,Elf32
from verify_gx8002_memcpy_source import decode
GLOBAL=0x2002734c
DEFAULT=0x20026bc8
ALTERNATE=0x20040000
CALLBACK=0x10204f18

def execute(code,entry,mode,initial,mutation,callback,result):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=mode,r14=0x20070000);saved=r.copy();stack={};trace=[];pointer=initial;reads=0;pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r15':raise ValueError('Public init frame')
            r['r14']-=4;stack[r['r14']]=r['r15']
        elif op=='pop':
            if args!='r15':raise ValueError('Public init restore')
            r['r15']=stack[r['r14']];r['r14']+=4
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Public init ABI')
            return r['r0'],trace,pointer
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups();address=r[base]+int(offset,0)
            if address==GLOBAL:
                if op=='ld.w':
                    reads+=1
                    if reads==2 and mutation is not None:pointer=mutation
                    r[reg]=pointer;trace.append(('read_global',pointer))
                else:
                    if r[reg]!=DEFAULT:raise ValueError('Default dispatch pointer')
                    pointer=r[reg];trace.append(('write_global',pointer))
            elif address in (DEFAULT+4,ALTERNATE+4) and op=='ld.w':r[reg]=callback;trace.append(('read_callback',address,callback))
            else:raise ValueError('Public init memory address')
        elif op in ('bsr','jsr'):
            if op=='bsr':
                target=(int(args,0)+(0x101f6a74 if entry==0xeabc else 0))&0xffffffff
                if target!=0x10206c24 or (r['r0'],r['r1'],r['r2'])!=(0x1020abfa,0x1020ab79,377):raise ValueError('Public init diagnostic arguments')
                trace.append(('diagnostic',0x1020abfa,0x1020ab79,377));returned=123
            else:
                if r[args]!=CALLBACK or r['r0']!=mode:raise ValueError('Public init callback arguments')
                trace.append(('callback',CALLBACK,mode));returned=result
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=returned
        else:raise ValueError('Public init opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Public init bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=sha(IMAGE.read_bytes()):raise ValueError('Public init stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xeabc','--stop-address=0xeb00',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-public-init/bits.disassembly.txt').read_text());cases=0
    for mode,initial,mutation,callback,result in product((0,1,2,3,0x80000000,0xffffffff),(0,DEFAULT,ALTERNATE),(None,0,DEFAULT,ALTERNATE),(0,CALLBACK),(0,1,0xffffffff,0x80000000)):
        pointer=initial;trace=[('read_global',pointer)]
        if not pointer:pointer=DEFAULT;trace.append(('write_global',pointer))
        if mutation is not None:pointer=mutation
        trace.append(('read_global',pointer))
        if not pointer:trace.append(('diagnostic',0x1020abfa,0x1020ab79,377));returned=0xffffffff
        else:
            trace.append(('read_callback',pointer+4,callback));returned=0
            if callback:trace.append(('callback',CALLBACK,mode));returned=result
        wanted=(returned,trace,pointer)
        for code,entry in ((old,0xeabc),(new,0x10205530)):
            if execute(code,entry,mode,initial,mutation,callback,result)!=wanted:raise ValueError(('Public init effects',entry,mode,initial,mutation,callback,result))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Callback/printf modeled with caller clobbers. Optional global replacement before second read; finite valid dispatch pointers. Hardware init callback, BSS lifecycle and concurrent mutation outside tested boundary remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-public-init-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
