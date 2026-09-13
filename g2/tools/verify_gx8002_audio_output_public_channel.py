# SPDX-License-Identifier: MIT
"""Decoded public-callback global rereads, indirect ABI and diagnostic arguments."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_public_channel import build,ROOT,IMAGE,sha,Elf32
from verify_gx8002_memcpy_source import decode
GLOBAL=0x2002734c
DEFAULT=0x20026bc8
ALTERNATE=0x20040000
CALLBACK=0x1020502c

def execute(code,entry,mode,config,initial,callback,result):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=mode,r1=config,r14=0x20070000);saved=r.copy();stack={};trace=[];pointer=initial;pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r15':raise ValueError('Public channel frame')
            r['r14']-=4;stack[r['r14']]=r['r15']
        elif op=='pop':
            if args!='r15':raise ValueError('Public channel restore')
            r['r15']=stack[r['r14']];r['r14']+=4
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Public channel ABI')
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
                    r[reg]=pointer;trace.append(('read_global',pointer))
                else:
                    raise ValueError('Allocation must not install dispatch')
            elif address in (DEFAULT+72,ALTERNATE+72) and op=='ld.w':r[reg]=callback;trace.append(('read_callback',address,callback))
            else:raise ValueError('Public channel memory address')
        elif op in ('bsr','jsr'):
            if op=='bsr':
                target=(int(args,0)+(0x101f6a74 if entry==0xea84 else 0))&0xffffffff
                if target!=0x10206c24 or (r['r0'],r['r1'],r['r2'])!=(0x1020abfa,0x1020ab60,365):raise ValueError('Public channel diagnostic arguments')
                trace.append(('diagnostic',0x1020abfa,0x1020ab60,365));returned=123
            else:
                if r[args]!=CALLBACK or (r['r0'],r['r1'])!=(mode,config):raise ValueError('Public channel callback arguments')
                trace.append(('callback',CALLBACK,mode,config));returned=result
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=returned
        else:raise ValueError('Public channel opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Public channel bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=sha(IMAGE.read_bytes()):raise ValueError('Public channel stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xea84','--stop-address=0xeabc',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-public-channel/bits.disassembly.txt').read_text());cases=0
    for route,config,pointer,callback,result in product((0,1,0x20026b94,0x7fffffff,0x80000000,0xffffffff),(*range(256),0x7fffffff,0x80000000,0xffffffff),(0,DEFAULT,ALTERNATE),(0,CALLBACK),(0,0x20026b94,0xffffffff,0x80000000)):
        trace=[('read_global',pointer)]
        if not pointer:trace.append(('diagnostic',0x1020abfa,0x1020ab60,365));returned=0xffffffff
        else:
            trace.append(('read_callback',pointer+72,callback));returned=0
            if callback:trace.append(('callback',CALLBACK,route,config));returned=result
        wanted=(returned,trace,pointer)
        for code,entry in ((old,0xea84),(new,0x102054f8)):
            if execute(code,entry,route,config,pointer,callback,result)!=wanted:raise ValueError(('Public channel effects',entry,route,pointer,callback,result))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Raw32-bit handle and channel-selector forwarding; callback and printf modeled with caller clobbers. Fixed valid dispatch pointers, original global slot. Underlying channel-selection effects and BSS lifecycle not qualified by this wrapper test.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-public-channel-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
