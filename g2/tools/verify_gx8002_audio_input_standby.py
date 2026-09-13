# SPDX-License-Identifier: MIT
"""Decode standby flags and ordered interrupt helper calls."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_standby import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,byte,result):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;events=[];pc=entry
    for _ in range(24):
        op,args,w=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('Frame')
            saved=r['r15'];r['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('Restore')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return byte,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='ixw':r[p[0]]=(r[p[1]]+4*r[p[2]])&0xffffffff
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low
            r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op in ('ld.b','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            if r[base]+int(off,0)!=0x2002ecc0:raise ValueError('Flag address')
            if op=='ld.b':r[reg]=byte;events.append(('read',byte))
            else:byte=r[reg]&255;events.append(('write',byte))
        elif op=='bsr':
            if (int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&0xffffffff!=0x102047b8:raise ValueError('Helper target')
            events.append(('interrupt',r['r0'],r['r1'],byte))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=result
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Bound')


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10bd0','--stop-address=0x10c0c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-standby/buffers.disassembly.txt').read_text());cases=0
    for byte,result in product(range(256),(0,1,0x80000000,0xffffffff)):
        changed=(byte&15)|16
        for code,base in ((old,0),(new,0x101f6a74)):
            if execute(code,0x10bd0+base,byte,result)!=(byte,[('interrupt',0x20007,0,byte),('interrupt',0x10000,1,byte)]):raise ValueError('Suspend')
            if execute(code,0x10bec+base,byte,result)!=(changed,[('read',byte),('write',changed),('interrupt',0x30007,1,changed)]):raise ValueError('Startup')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['All flag bytes, ordered interrupt arguments, caller clobbers and saved ABI checked. Interrupt helper modeled; physical standby/timing and admission pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-standby-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
