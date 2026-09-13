# SPDX-License-Identifier: MIT
"""Decode by-value Spectrum output parameters and separate ordered register field writes."""
import json,re,random,subprocess
from itertools import product
from build_gx8002_audio_output_spectrum import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_pcm_channel_setting import execute as setting,verify as setting_verify
STACK=0x20070000


def execute(code,entry,parameters,word,state):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update({f'r{i}':parameters[i] for i in range(4)});r['r14']=STACK
    initial=r.copy();memory={STACK:parameters[4],STACK+4:parameters[5],0xa0a00108:word,0x20027334:state};trace=[];pc=entry;condition=False;pushed=False
    for _ in range(120):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if pushed or args!='r4-r7, r15':raise ValueError('Spectrum output saved frame')
            r['r14']-=20
            for i,name in enumerate(('r4','r5','r6','r7','r15')):memory[r['r14']+4*i]=r[name]
            pushed=True
        elif op=='rts':
            if not pushed or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Spectrum output ABI restore')
            if (memory[STACK],memory[STACK+4])!=parameters[4:]:raise ValueError('Spectrum output caller stack overwritten')
            return r['r0'],trace,{address:memory[address] for address in (0xa0a00108,0x20027334)}
        elif op in ('mov','movi','lrw','movih'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='ldm':
            if args!='r4-r7, (r14)':raise ValueError('Spectrum output ldm frame')
            for i in range(4):r[f'r{i+4}']=memory[r['r14']+i*4]
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('or','ori'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=a|b
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('Spectrum output memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&0xffffffff
            stack=STACK-36<=address<=STACK+4 and address%4==0
            if address not in (0xa0a00108,0x20027334) and not stack:raise ValueError('Spectrum output memory bounds')
            if op=='ld.w':
                if address not in memory:raise ValueError('Spectrum output uninitialized stack read')
                r[reg]=memory[address]
                if not stack:trace.append(('read',address,r[reg]))
            else:
                memory[address]=r[reg]
                if not stack:trace.append(('write',address,r[reg]))
        elif op=='bsr':
            delta=0x101f6a74 if entry==0xd6b8 else 0
            target=(int(args,0)+delta)&0xffffffff
            if target!=0x10203dc8:raise ValueError('PCM setting target')
            arguments=(r['r0'],r['r1'],r['r2'],r['r3'],memory[r['r14']])
            trace.append(('setting',*arguments))
            result,nested=setting(code,0xd354 if entry==0xd6b8 else 0x10203dc8,*arguments)
            trace.extend(nested)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Spectrum output instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Spectrum output bound')


def verify():
    candidate=build();dependency=setting_verify();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Spectrum output stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd354','--stop-address=0xd7b4',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-output-spectrum/spectrum.disassembly.txt').read_text())
    new.update(decode((ROOT/'build/gx8002-board/pcm-channel-setting-candidate.disassembly.txt').read_text()));cases=0
    for channel,buffer,size,frames,endian,source,word,state in product((0,1,2,3,4,0xffffffff),(0,0x20050000,0x20050001,0x20050007),(0,127,128,0xffffff80),(0,1,0x80000000,0xffffffff),(0,1,0xffffffff),(0,4,7,0xffffffff),(0,0xffffffff),(0,0xffffffff)):
        parameters=(channel,buffer,size,frames,endian,source);trace=[];w=word;s=state;result=0xffffffff
        # This write occurs even when validation fails.
        trace.append(('read',0xa0a00108,w));w=(w&~0x70000)|((source&7)<<16);trace.append(('write',0xa0a00108,w))
        if not (buffer%8 or size%128) and channel in (1,2):
            index=channel-1;count=(frames*2)&0xffffffff
            trace.append(('setting',index,buffer,0,size,count))
            base=0xa0a00000+index*36
            trace.extend([('write',base+0x110,count),('write',base+0x114,buffer),('write',base+0x11c,0),('write',base+0x120,size),('write',0xa0a00104,1<<(index+11))])
            for low,bits,value in ((index*8,2,3),(index*8+2,2,endian),(index*8+6,1,1),(index*8+7,1,0),(index*8+5,1,1)):
                trace.append(('read',0xa0a00108,w));mask=((1<<bits)-1)<<low;w=(w&~mask)|((value<<low)&mask);trace.append(('write',0xa0a00108,w))
            trace.extend([('read',0x20027334,s),('write',0x20027334,s|channel)]);s|=channel;result=0
        wanted=(result,trace,{0xa0a00108:w,0x20027334:s})
        if execute(old,0xd6b8,parameters,word,state)!=wanted or execute(new,0x1020412c,parameters,word,state)!=wanted:raise ValueError('Spectrum output nested oracle')
        cases+=1
    return {'candidate':candidate,'setting_dependency':dependency,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Pinned SDK aggregate and nested buffer helper execute decoded code in separate frames. Source selection changes before validation, including invalid calls. Frame count doubling wraps modulo 32 bits. Ordered field writes and full stack ABI checked; physical spectrum delivery unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-spectrum-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Spectrum output cases:',r['decoded_cases'])
